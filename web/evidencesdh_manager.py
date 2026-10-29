#!/usr/bin/env python3
import argparse
import getpass
import sys
import time
from html.parser import HTMLParser
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from urllib.parse import urljoin
from urllib.parse import urlparse

import requests

BASE = 'https://www.evidencesdh.cz'
ROOT_PATH = '/index.php/'
LOGIN_PAGE = '/index.php/login'
GA_POST = '/index.php/sdh_auth/ga'
FIRE_BRIGADE_LIST = '/index.php/fire_brigade'  # New constant

VERBOSE = True  # set False with --quiet


def vprint(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


def show_resp(prefix: str, resp: requests.Response, show_set_cookie=False):
    vprint(f"{prefix}: {resp.request.method} {resp.request.url} -> "
           f"{resp.status_code} {resp.reason}")
    if VERBOSE:
        vprint('  Content-Type:', resp.headers.get('Content-Type'))
        if show_set_cookie:
            for k, v in resp.headers.items():
                if k.lower() == 'set-cookie':
                    vprint('  Set-Cookie:', v)


BASE_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/144.0.0.0 Safari/537.36'
    ),
    'Accept': (
        'text/html,application/xhtml+xml,application/xml;q=0.9,'
        'image/avif,image/webp,image/apng,*/*;q=0.8,'
        'application/signed-exchange;v=b3;q=0.7'
    ),
    'Accept-Language': 'en',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# ----------------------------
# Login form parsing utilities
# ----------------------------


class SigninForm:
    def __init__(self):
        self.action: str = LOGIN_PAGE  # default; replaced if found
        self.method: str = 'post'
        self.inputs: Dict[str, str] = {}
        # any input with name starting with signin[
        self.has_signin_field: bool = False

    def __repr__(self):
        return (
            f"<SigninForm action={self.action!r} "
            f"method={self.method!r} "
            f"inputs={list(self.inputs.keys())!r}>"
        )


class LoginFormParser(HTMLParser):
    """
    Locate the login <form> that carries inputs named 'signin[...]'.
    Capture action, method and all inputs (hidden + others).
    """

    def __init__(self):
        super().__init__()
        self.in_form = False
        self.current_form_attrs: Dict[str, str] = {}
        self.current_inputs: Dict[str, str] = {}
        self.current_has_signin = False
        self.captured: Optional[SigninForm] = None
        self.form_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = {k.lower(): (v or '') for k, v in attrs}
        if tag.lower() == 'form':
            if not self.in_form:
                self.in_form = True
                self.form_depth = 1
                self.current_form_attrs = attrs_dict
                self.current_inputs = {}
                self.current_has_signin = False
            else:
                self.form_depth += 1
        elif tag.lower() == 'input' and self.in_form:
            name = attrs_dict.get('name')
            value = attrs_dict.get('value') or ''
            if name:
                self.current_inputs[name] = value
                if name.startswith('signin['):
                    self.current_has_signin = True
                if name in {
                    '_csrf_token',
                    'csrf_token',
                    'signin[_csrf_token]',
                }:
                    self.current_has_signin = True

    def handle_endtag(self, tag):
        if tag.lower() == 'form' and self.in_form:
            self.form_depth -= 1
            if self.form_depth == 0:
                if self.current_has_signin and self.captured is None:
                    f = SigninForm()
                    # Split over multiple lines to satisfy E501
                    act = self.current_form_attrs.get('action')
                    f.action = act or LOGIN_PAGE

                    met = self.current_form_attrs.get('method')
                    f.method = (met or 'post').lower()

                    f.inputs = dict(self.current_inputs)
                    f.has_signin_field = True
                    self.captured = f
                # reset
                self.in_form = False
                self.current_form_attrs = {}
                self.current_inputs = {}

    def get_form(self) -> Optional[SigninForm]:
        return self.captured


def parse_login_form(html: str) -> Optional[SigninForm]:
    if not html:
        return None
    p = LoginFormParser()
    try:
        p.feed(html)
    except Exception:
        return None
    return p.get_form()


def merge_payload(
    form_inputs: Dict[str, str],
    username: str,
    password: str,
) -> Dict[str, str]:
    payload = dict(form_inputs or {})
    payload['signin[username]'] = username
    payload['signin[password]'] = password
    payload.setdefault('signin[authtype]', 'ga')
    payload.setdefault('signin[remember]', 'onrequest')
    return payload


# ----------------------------
# Link discovery parsers
# ----------------------------
class AnchorCollector(HTMLParser):
    def __init__(self, base: str):
        super().__init__()
        self.base = base
        self.links: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != 'a':
            return
        attrs_dict = {k.lower(): v for k, v in attrs}
        href = attrs_dict.get('href')
        if not href:
            return
        self.links.append(urljoin(self.base, href))


def find_unique_txt_on_page(html: str, base_url: str) -> Optional[str]:
    """
    Return the single /index.php/fire_brigade_print/*.txt link on this page,
    or None if 0 or >1 exist.
    """
    if not html:
        return None
    c = AnchorCollector(base_url)
    try:
        c.feed(html)
    except Exception:
        return None
    matches = [
        u for u in c.links
        if '/index.php/fire_brigade_print/' in urlparse(u).path
        and urlparse(u).path.lower().endswith('.txt')
    ]
    uniq = list(dict.fromkeys(matches))  # de-dup while preserving order
    if len(uniq) == 1:
        return uniq[0]
    return None


def find_single_listshow_link(html: str, base_url: str) -> Optional[str]:
    """
    If the landing page doesn't have the .txt link directly,
    try to find a single '/index.php/fire_brigade/<NUM>/ListShow' link.
    """
    if not html:
        return None
    c = AnchorCollector(base_url)
    try:
        c.feed(html)
    except Exception:
        return None
    candidates = []
    for u in c.links:
        p = urlparse(u).path
        if p.startswith('/index.php/fire_brigade/') and \
           p.endswith('/ListShow'):
            candidates.append(u)
    uniq = list(dict.fromkeys(candidates))
    if len(uniq) == 1:
        return uniq[0]
    return None


def extract_unit_id_from_listshow(url: str) -> Optional[str]:
    """
    Extracts '6240' from '.../index.php/fire_brigade/6240/ListShow'.
    """
    try:
        path = urlparse(url).path
        # path is like /index.php/fire_brigade/6240/ListShow
        parts = path.split('/')
        if parts[-1] == 'ListShow':
            return parts[-2]
    except Exception:
        pass
    return None


class FireBrigadeListParser(HTMLParser):
    """
    Collect links like /index.php/fire_brigade/<ID>/ListShow together with
    their visible anchor text (e.g. 'SDH Morávka').
    """

    def __init__(self, base: str):
        super().__init__()
        self.base = base
        self.items: List[Tuple[str, str]] = []
        self._in_target_a = False
        self._current_href: Optional[str] = None
        self._text_parts: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != 'a':
            return
        attrs_dict = {k.lower(): (v or '') for k, v in attrs}
        href = attrs_dict.get('href')
        if not href:
            return

        abs_url = urljoin(self.base, href)
        p = urlparse(abs_url).path
        if (
            p.startswith('/index.php/fire_brigade/') and
            p.endswith('/ListShow')
        ):
            self._in_target_a = True
            self._current_href = abs_url
            self._text_parts = []

    def handle_data(self, data):
        if self._in_target_a:
            self._text_parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == 'a' and self._in_target_a:
            text = ' '.join(''.join(self._text_parts).split()).strip()
            if self._current_href:
                self.items.append((self._current_href, text))
            self._in_target_a = False
            self._current_href = None
            self._text_parts = []


def find_single_listshow_entry(
    html: str,
    base_url: str,
) -> Optional[Tuple[str, str]]:
    """
    Returns a single (listshow_url, anchor_text) entry if exactly one unique
    ListShow link is present, else None.
    """
    if not html:
        return None

    p = FireBrigadeListParser(base_url)
    try:
        p.feed(html)
    except Exception:
        return None

    # dedup by URL, preserve first text
    dedup: Dict[str, str] = {}
    for u, t in p.items:
        if u not in dedup:
            dedup[u] = t

    if len(dedup) == 1:
        u = next(iter(dedup.keys()))
        return u, dedup[u]
    return None


def process_download(username, password, ga_code):
    """
    Reusable function for Flask or other callers.
    Returns (filename, content_bytes) on success.
    Raises Exception on failure.
    """
    with requests.Session() as s:
        s.headers.update(BASE_HEADERS)

        # 0) Open root
        r_root = s.get(
            urljoin(BASE, ROOT_PATH),
            timeout=20, allow_redirects=True,
        )
        form = parse_login_form(r_root.text)

        # 0b) Try explicit login page
        r_login = s.get(
            urljoin(BASE, LOGIN_PAGE),
            timeout=20, allow_redirects=True,
        )
        f2 = parse_login_form(r_login.text)
        if f2:
            form = f2

        # Decide action/method and build payload
        if form:
            action_url = urljoin(BASE, form.action)
            method = form.method or 'post'
            discovered_inputs = form.inputs
        else:
            action_url = urljoin(BASE, LOGIN_PAGE)
            method = 'post'
            discovered_inputs = {}

        payload = merge_payload(discovered_inputs, username, password)

        # 1) LOGIN POST #1
        s.headers.update({
            'Origin': BASE,
            'Referer': urljoin(BASE, LOGIN_PAGE),
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        if method == 'post':
            r1 = s.post(
                action_url, data=payload,
                timeout=20, allow_redirects=False,
            )
        else:
            r1 = s.get(
                action_url, params=payload,
                timeout=20, allow_redirects=False,
            )

        # Retry once with freshly parsed hidden fields if needed
        if r1.status_code not in (302, 303):
            f_retry = parse_login_form(r1.text or '')
            if f_retry:
                payload2 = merge_payload(f_retry.inputs, username, password)
                action_url2 = urljoin(BASE, f_retry.action)
                method2 = f_retry.method or 'post'
                time.sleep(0.3)
                if method2 == 'post':
                    r1b = s.post(
                        action_url2, data=payload2,
                        timeout=20, allow_redirects=False,
                    )
                else:
                    r1b = s.get(
                        action_url2, params=payload2,
                        timeout=20, allow_redirects=False,
                    )
                r1 = r1b

        if r1.status_code not in (302, 303):
            raise Exception(
                f"Login failed (status {r1.status_code}). "
                f"Response snippet: {(r1.text or '')[:200]}",
            )

        # Follow login redirect
        loc1 = r1.headers.get('Location', '')
        if not loc1:
            raise Exception('Login redirect missing Location header.')

        message_url = urljoin(BASE, loc1)
        # r_after_login = s.get(message_url, timeout=20, allow_redirects=True)

        # 2) Two-factor (GA)
        s.headers.update({
            'Origin': BASE,
            'Referer': message_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        r2 = s.post(
            urljoin(BASE, GA_POST),
            data={'secure': ga_code},
            timeout=20, allow_redirects=False,
        )

        if r2.status_code not in (302, 303):
            raise Exception(
                f"2FA failed (status {r2.status_code}). Check code.",
            )

        loc2 = r2.headers.get('Location', '')
        if not loc2:
            raise Exception('2FA redirect missing Location header.')

        # Follow redirect just to complete login flow cookies
        # (usually to dashboard)
        after_login_url = urljoin(BASE, loc2)
        r2_follow = s.get(after_login_url, timeout=20, allow_redirects=True)
        vprint(f"  [debug] Landed on: {r2_follow.url}")

        # 3) Updated Logic: Go to fire_brigade list to find Unit ID
        fb_url = urljoin(BASE, FIRE_BRIGADE_LIST)
        r_fb = s.get(fb_url, timeout=20, allow_redirects=True)
        vprint(f"  [debug] Fetched Fire Brigade List: {r_fb.url}")

        entry = find_single_listshow_entry(r_fb.text or '', fb_url)
        if not entry:
            raise Exception(
                f"Could not find a single LinkShow link on {fb_url}.",
            )

        listshow_url, brigade_name = entry

        unit_id = extract_unit_id_from_listshow(listshow_url)
        if not unit_id:
            raise Exception(
                f"Could not extract unit ID from link: {listshow_url}",
            )

        vprint(f"  [debug] Found Unit ID: {unit_id}")
        vprint(f"  [debug] Found Unit Name: {brigade_name}")

        txt_url = urljoin(
            BASE, f"/index.php/fire_brigade_print/{unit_id}.txt",
        )
        file_name = f"{(brigade_name or unit_id).strip()}.txt"

        vprint(f"  [debug] Constructing download URL: {txt_url}")

        # 4) Fetch the discovered .txt
        r_txt = s.get(txt_url, timeout=30, allow_redirects=False)

        if r_txt.status_code == 200 and 'text' in (
            r_txt.headers.get('Content-Type', '').lower()
        ):
            r_txt.encoding = r_txt.encoding or 'utf-8'
            return file_name, r_txt.text
        else:
            raise Exception(
                f"Download failed for {txt_url}: status={r_txt.status_code}",
            )


# ----------------------------
# Main flow
# ----------------------------
def main():
    parser = argparse.ArgumentParser(
        description='Login + discover the single TXT file + download',
    )
    parser.add_argument(
        '--out', type=str, default=None,
        help='Optional output filename; default: extracted from link',
    )
    parser.add_argument(
        '--quiet', action='store_true',
        help='Reduce log noise',
    )
    args = parser.parse_args()

    global VERBOSE
    if args.quiet:
        VERBOSE = False

    print(
        '=== Evidencesdh.cz login + discover & download (no ID needed) ===',
    )

    username = input('Username (email): ').strip()
    password = getpass.getpass('Password: ').strip()
    if not username or not password:
        print('Username and password are required.', file=sys.stderr)
        sys.exit(1)

    # Re-implement CLI using the new helper
    try:
        ga_code = input('Enter 2FA code (Google Authenticator): ').strip()
        fname, content = process_download(username, password, ga_code)

        out_path = args.out or fname
        print(f"[i] Will save as:    {out_path}")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[ok] Saved {len(content)} chars to {out_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print('\nDone.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nAborted by user.')
