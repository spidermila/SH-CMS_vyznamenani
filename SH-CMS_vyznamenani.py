'''Program pro vytvoření přehledu vyznamenání členů SDH SH-ČMS'''
import argparse
import os
from datetime import datetime

from libs.hasici import Hasici
from libs.xlsxwriter import Xlsxwriter


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-h',
        '--help',
        action='help',
        default=argparse.SUPPRESS,
        help='zobraz tuto nápovědu',
    )
    parser.add_argument(
        'soubor',
        help='textovy soubor exportovany z evidencesdh.cz',
    )
    parser.add_argument(
        '-r',
        '--rok',
        type=int,
        default=datetime.now().year,
        help='rok ke kterému se budou kontrolovat splněné podmínky',
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='test.xlsx',
        help='název xlsx souboru, do kterého se zapíše výsledek',
    )
    args = parser.parse_args()

    if not os.path.isfile(args.soubor):
        print(f'Soubor {args.soubor} neexistuje!')
        return 1

    if args.output.lower()[-5:] != '.xlsx':
        print('Výstupní soubor musí mít příponu .xlsx!')
        return 1

    lines = []
    try:
        with open(args.soubor, encoding='UTF-8') as fp:
            for line in fp:
                lline = line.strip().split(' ')
                if len(lline) > 0:
                    lines.append(lline)

    hasici = Hasici()
    hasici.create_hasici_from_export(lines)

    w = Xlsxwriter(hasici.hasici)
    w.write(args.output)
    return 0


if __name__ == '__main__':
    raise (SystemExit(main()))
