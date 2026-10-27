import contextlib
import os
import tempfile

import pandas as pd  # type: ignore
from openpyxl.styles import Alignment  # type: ignore
from openpyxl.styles import PatternFill  # type: ignore

from libs.hasic import Hasic


class Xlsxwriter:
    def __init__(self, hasici: list[Hasic]) -> None:
        self.hasici = hasici

    def write(self, soubor: str, rok: int) -> None:
        data = {}
        for hasic in self.hasici:
            zaznamy = {}
            for vyz in hasic.vyznamenani:
                zaznamy[vyz.nazev] = ', '.join(
                    vyz.splnene_podminky(hasic, rok),
                )
            data[hasic.jmeno] = zaznamy
        df = pd.DataFrame(data)
        transposed = df.T
        # ponytail: mkstemp makes the file 0600, os.replace keeps that mode
        fd, tmp = tempfile.mkstemp(
            suffix='.xlsx',
            dir=os.path.dirname(os.path.abspath(soubor)),
        )
        try:
            with os.fdopen(fd, 'wb') as f:
                writer = pd.ExcelWriter(f, engine='openpyxl')
                transposed.to_excel(
                    writer,
                    sheet_name='splnene podminky',
                    header=True,
                    index=True,
                )
                ws = writer.sheets['splnene podminky']
                for row in range(1, ws.max_row + 1):
                    for col in range(1, ws.max_column + 1):
                        _cell = ws.cell(column=col, row=row)
                        _cell.alignment = Alignment(wrap_text=True)
                        if _cell.value:
                            if (
                                'Obdrženo' in _cell.value or
                                'Již se nedává' in _cell.value
                            ):
                                _cell.fill = PatternFill(
                                    start_color='00969696',
                                    fill_type='solid',
                                )
                            elif 'Podmínky splněny' in _cell.value:
                                _cell.fill = PatternFill(
                                    start_color='00CCFFCC',
                                    fill_type='solid',
                                )
                ws.freeze_panes = ws['A2']
                writer.close()
            while True:
                try:
                    os.replace(tmp, soubor)
                    break
                except PermissionError:
                    print(
                        f'Soubor {soubor} je používán jinou aplikací.' +
                        'Zavřete soubor a stiskněte Enter.',
                    )
                    input()
        except BaseException:
            with contextlib.suppress(OSError):
                os.remove(tmp)
            raise
