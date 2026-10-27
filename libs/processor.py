import io
from datetime import datetime

from libs.hasici import Hasici
from libs.xlsxwriter import Xlsxwriter


class PrazdnyExportError(ValueError):
    '''Export neobsahuje žádného platného člena.'''


def process_txt_content(txt_content: str, rok: int | None = None) -> bytes:
    '''Process evidencesdh.cz export text and return XLSX bytes.'''
    lines = [line.strip().split(' ') for line in txt_content.splitlines()]
    hasici = Hasici()
    hasici.create_hasici_from_export(lines)
    if not hasici.hasici:
        raise PrazdnyExportError
    output = io.BytesIO()
    Xlsxwriter(hasici.hasici).write(output, rok or datetime.now().year)
    return output.getvalue()
