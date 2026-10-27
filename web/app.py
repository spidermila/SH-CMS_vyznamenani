import io
import json
import logging
import os
import re
import secrets
import time
import uuid
from pathlib import Path
from threading import Lock

from flask import Flask
from flask import render_template
from flask import request
from flask import send_file
from flask import session
from flask import url_for
from werkzeug.utils import secure_filename

from libs.processor import process_txt_content
from web import evidencesdh_manager

app = Flask(__name__)

log_level = os.getenv('APP_LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
)
app.logger.setLevel(getattr(logging, log_level, logging.INFO))

app.secret_key = os.environ.get('APP_SECRET_KEY') or secrets.token_hex(32)

TTL_SECONDS = 5 * 60  # 5 minutes
MAX_TEMP_FILES = 100
MAX_XLSX_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_USERNAME_LEN = 254
MAX_PASSWORD_LEN = 256

# Shared on-disk cache (visible to all gunicorn workers in the same container)
CACHE_DIR = Path('/tmp/shcms-cache')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Best-effort in-memory rate limiting (still per-process).
RATE_WINDOW_SECONDS = 60
RATE_MAX_REQUESTS = 20
RATE_LIMIT_STORAGE: dict[str, list[float]] = {}
RATE_LIMIT_LOCK = Lock()

# Request body limit
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024  # 16 KB


def _meta_path(file_id: str) -> Path:
    return CACHE_DIR / f'{file_id}.json'


def _xlsx_path(file_id: str) -> Path:
    return CACHE_DIR / f'{file_id}.xlsx'


def _get_owner_token() -> str:
    token = session.get('owner_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['owner_token'] = token
    return token


def _save_cached_file(
    file_id: str,
    xlsx_bytes: bytes,
    safe_name: str,
    owner_token: str,
) -> None:
    xlsx_path = _xlsx_path(file_id)
    meta_path = _meta_path(file_id)

    xlsx_path.write_bytes(xlsx_bytes)
    meta = {
        'name': safe_name,
        'created_at': time.time(),
        'owner_token': owner_token,
    }
    meta_path.write_text(json.dumps(meta), encoding='utf-8')


def _load_cached_meta(file_id: str) -> dict | None:
    meta_path = _meta_path(file_id)
    if not meta_path.exists():
        return None
    try:
        return json.loads(meta_path.read_text(encoding='utf-8'))
    except Exception:
        return None


def cleanup_old_files() -> None:
    now = time.time()
    for meta_path in CACHE_DIR.glob('*.json'):
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            created_at = float(meta.get('created_at', 0))
            if now - created_at > TTL_SECONDS:
                file_id = meta_path.stem
                _xlsx_path(file_id).unlink(missing_ok=True)
                meta_path.unlink(missing_ok=True)
        except Exception:
            # Broken metadata -> delete best effort
            file_id = meta_path.stem
            _xlsx_path(file_id).unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)


def _count_cached_files() -> int:
    return sum(1 for _ in CACHE_DIR.glob('*.json'))


def _client_ip() -> str:
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    with RATE_LIMIT_LOCK:
        timestamps = RATE_LIMIT_STORAGE.get(ip, [])
        timestamps = [t for t in timestamps if now - t <= RATE_WINDOW_SECONDS]
        if len(timestamps) >= RATE_MAX_REQUESTS:
            RATE_LIMIT_STORAGE[ip] = timestamps
            return True
        timestamps.append(now)
        RATE_LIMIT_STORAGE[ip] = timestamps
        return False


def _validate_input(username: str, password: str, ga_code: str) -> str | None:
    if len(username) > MAX_USERNAME_LEN:
        return 'Uživatelské jméno je příliš dlouhé.'
    if len(password) > MAX_PASSWORD_LEN:
        return 'Heslo je příliš dlouhé.'
    if '\x00' in username or '\x00' in password or '\x00' in ga_code:
        return 'Neplatný vstup.'
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', username):
        return 'Neplatný formát emailu.'
    if not re.fullmatch(r'\d{6}', ga_code):
        return '2FA kód musí mít 6 číslic.'
    return None


@app.after_request
def add_security_headers(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Referrer-Policy'] = 'no-referrer'
    resp.headers['Cache-Control'] = 'no-store'
    return resp


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ip = _client_ip()
        if _is_rate_limited(ip):
            return render_template(
                'index.html',
                error='Příliš mnoho požadavků. Zkuste to prosím za chvíli.',
                success_msg=None,
                download_link=None,
            ), 429

        cleanup_old_files()

        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        ga_code = (request.form.get('ga_code') or '').strip()

        if not username or not password or not ga_code:
            return render_template(
                'index.html',
                error='Všechny pole jsou povinná.',
                success_msg=None,
                download_link=None,
            )

        validation_error = _validate_input(username, password, ga_code)
        if validation_error:
            return render_template(
                'index.html',
                error=validation_error,
                success_msg=None,
                download_link=None,
            ), 400

        try:
            filename, file_content = evidencesdh_manager.process_download(
                username, password, ga_code,
            )
            xlsx_bytes = process_txt_content(file_content)

            if len(xlsx_bytes) > MAX_XLSX_BYTES:
                raise ValueError('Vygenerovaný soubor je příliš velký.')

            if _count_cached_files() >= MAX_TEMP_FILES:
                raise RuntimeError(
                    'Server je dočasně vytížen. Zkuste to prosím později.',
                )

            original_name = filename.replace('.txt', '.xlsx')
            safe_name = secure_filename(original_name) or 'vysledek.xlsx'
            file_id = uuid.uuid4().hex
            owner_token = _get_owner_token()

            _save_cached_file(file_id, xlsx_bytes, safe_name, owner_token)

            return render_template(
                'index.html',
                error=None,
                success_msg='Soubor byl úspěšně vygenerován.',
                download_link=url_for('download_file', file_id=file_id),
            )
        except Exception:
            logging.exception('Processing failed')
            return render_template(
                'index.html',
                error=(
                    'Nepodařilo se zpracovat požadavek. '
                    'Zkontrolujte údaje a zkuste to znovu.'
                ),
                success_msg=None,
                download_link=None,
            ), 500

    return render_template(
        'index.html',
        error=None,
        success_msg=None,
        download_link=None,
    )


@app.route('/download/<file_id>', methods=['GET', 'POST'])
def download_file(file_id: str):
    ip = _client_ip()
    if _is_rate_limited(ip):
        return render_template(
            'index.html',
            error='Příliš mnoho požadavků. Zkuste to prosím za chvíli.',
            success_msg=None,
            download_link=None,
        ), 429

    cleanup_old_files()

    if not re.fullmatch(r'[0-9a-f]{32}', file_id):
        return render_template(
            'index.html',
            error='Soubor vypršel. Vygenerujte prosím nový.',
            success_msg=None,
            download_link=None,
        ), 404

    meta = _load_cached_meta(file_id)
    xlsx_path = _xlsx_path(file_id)
    if not meta or not xlsx_path.exists():
        return render_template(
            'index.html',
            error='Soubor vypršel. Vygenerujte prosím nový.',
            success_msg=None,
            download_link=None,
        ), 404

    if meta.get('owner_token') != session.get('owner_token'):
        return render_template(
            'index.html',
            error='Tento soubor nelze stáhnout z aktuální relace.',
            success_msg=None,
            download_link=None,
        ), 403

    return send_file(
        io.BytesIO(xlsx_path.read_bytes()),
        as_attachment=True,
        download_name=meta.get('name', 'vysledek.xlsx'),
        mimetype=(
            'application/vnd.openxmlformats-'
            'officedocument.spreadsheetml.sheet'
        ),
    )


@app.errorhandler(405)
def method_not_allowed(_e):
    app.logger.warning('405 method=%s path=%s', request.method, request.path)
    return render_template(
        'index.html',
        error='Nepodporovaná metoda požadavku.',
        success_msg=None,
        download_link=None,
    ), 405
