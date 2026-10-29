import pytest  # type: ignore

from libs.hasic import Hasic

YEAR = 2025

EXPORT = '''Karel Zkusebni
==========================
Adresa 1
- 01.01.1960: Datum narození
- 65: Věk
- 01.01.1980: Členem SHČMS od
- Hasič: Stav členství
- 1990: Čestné uznání SDH
- 1995, 2000: Medaile Za zásluhy

Jana Vymyslena
==========================
- 02.02.2000: Datum narození
- 25: Věk
- 03.03.2015: Členem SHČMS od
- 2010: Funkce
'''


@pytest.fixture
def make_hasic():
    def make(narozen=1960, clenem=1980, **awards):
        h = Hasic()
        h.datum_narozeni = f'01.01.{narozen}'
        h.clenem_od = f'01.01.{clenem}'
        for attr, year in awards.items():
            vyz = getattr(h, attr)
            vyz.obdrzene = True
            vyz.obdrzene_rok = year
        return h
    return make


def cell(ws, header, row=2):
    for col in range(1, ws.max_column + 1):
        if ws.cell(row=1, column=col).value == header:
            return ws.cell(row=row, column=col)
    raise AssertionError(header)


@pytest.fixture
def export_file(tmp_path):
    path = tmp_path / 'export.txt'
    path.write_text(EXPORT, encoding='UTF-8')
    return path
