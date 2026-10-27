import pytest  # type: ignore
from conftest import EXPORT  # type: ignore
from conftest import YEAR  # type: ignore

from libs.hasici import Hasici


def parse(text):
    lines = [x.strip().split(' ') for x in text.splitlines()]
    h = Hasici()
    h.create_hasici_from_export(lines)
    return h


def test_parse_two():
    karel, jana = parse(EXPORT).hasici
    assert karel.jmeno == 'Karel Zkusebni'
    assert karel.datum_narozeni == '01.01.1960'
    assert karel.vek == 65
    assert karel.clenem_od == '01.01.1980'
    assert karel.cestne_uznani_sdh.obdrzene_rok == 1990
    assert karel.medaile_za_zasluhy.obdrzene_rok == 2000
    assert [x.nazev for x in karel.vyznamenani if x.obdrzene] == [
        'Čestné uznání SDH', 'Medaile Za zásluhy',
    ]
    assert jana.jmeno == 'Jana Vymyslena'
    assert jana.vek == 25
    assert jana.clenem_od == '03.03.2015'
    assert not any(x.obdrzene for x in jana.vyznamenani)


def test_parse_single():
    first_block = '\n'.join(EXPORT.splitlines()[:9])
    hasici = parse(first_block + '\nkonec\n').hasici
    assert [x.jmeno for x in hasici] == ['Karel Zkusebni']


def test_print_all(capsys):
    parse(EXPORT).print_all()
    out = capsys.readouterr().out
    assert 'hasici a jiz ziskane vyznamenani:' in out
    assert 'Karel Zkusebni' in out


def test_print_splnene_podminky_all(capsys):
    parse(EXPORT).print_splnene_podminky_all(YEAR)
    out = capsys.readouterr().out
    assert 'Splněné podmínky:' in out
    assert 'Jana Vymyslena 2000' in out


def test_print_splnene_podminky(capsys):
    parse(EXPORT).print_splnene_podminky(YEAR)
    out = capsys.readouterr().out
    assert 'Splnene podminky:' in out
    assert 'Karel Zkusebni' in out


def test_hasic_helpers():
    karel = parse(EXPORT).hasici[0]
    text = repr(karel)
    assert 'Karel Zkusebni' in text
    assert '65 let' in text
    assert 'Čestné uznání SDH - 1990' in text
    assert karel.get_owned_vyznamenani() == [
        {'Čestné uznání SDH': 1990}, {'Medaile Za zásluhy': 2000},
    ]
    splnene = karel.get_splnene_podminky(YEAR)
    assert 'Čestné uznání OSH - MSH' in splnene
    assert 'Čestné uznání SDH' not in splnene


HEAD = [
    'Karel Zkusebni',
    '==========================',
    '- 01.01.1960: Datum narození',
    '- 01.01.1980: Členem SHČMS od',
]


def block(*extra, head=HEAD):
    return '\n'.join([*head, *extra])


def test_last_line_processed():
    h = parse(block('- 2000: Čestné uznání SDH')).hasici[0]
    assert h.cestne_uznani_sdh.obdrzene is True
    assert h.cestne_uznani_sdh.obdrzene_rok == 2000


def test_empty_input():
    assert parse('').hasici == []


def test_short_dash_lines(capsys):
    h = parse(block('-', '- x', '- 1990: Čestné uznání SDH')).hasici[0]
    out = capsys.readouterr().out
    assert 'Varování: řádek 5 přeskočen: -' in out
    assert 'Varování: řádek 6 přeskočen: - x' in out
    assert h.cestne_uznani_sdh.obdrzene_rok == 1990


@pytest.mark.parametrize(
    'line', [
        '- abc: Medaile Za zásluhy',
        '- 1995, x: Medaile Za zásluhy',
        '- x: Věk',
    ],
)
def test_bad_values(capsys, line):
    h = parse(block(line)).hasici[0]
    assert f'Varování: řádek 5 přeskočen: {line}' in capsys.readouterr().out
    assert h.medaile_za_zasluhy.obdrzene is False
    assert h.vek == 0


@pytest.mark.parametrize('head', [HEAD[:3], [*HEAD[:2], HEAD[3]]])
def test_member_without_dates(capsys, head):
    assert parse(block(head=head)).hasici == []
    assert 'Karel Zkusebni nemá datum narození/členství' in (
        capsys.readouterr().out
    )


@pytest.mark.parametrize(
    'line', [
        '- 01.01.abcd: Datum narození',
        '- 01.01.abcd: Členem SHČMS od',
    ],
)
def test_bad_dates(capsys, line):
    assert parse(block(line, head=HEAD[:2])).hasici == []
    out = capsys.readouterr().out
    assert f'Varování: řádek 3 přeskočen: {line}' in out
    assert 'nemá datum narození/členství' in out


def test_mezinar_spolupraci3():
    line = '- 2010: Medaile Za mezinárodní spolupráci III. stupně'
    h = parse(block(line)).hasici[0]
    vyz = h.medaile_za_mezinar_spolupraci3
    assert (vyz.obdrzene, vyz.obdrzene_rok) == (True, 2010)
    assert Hasici().retezce['medaile_za_mezinar_spolupraci3'] == vyz.nazev
