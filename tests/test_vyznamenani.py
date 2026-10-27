import itertools

import pytest  # type: ignore
from conftest import YEAR  # type: ignore

from libs.vyznamenani import Vyznamenani

SDH = 'Čestné uznání SDH'
OSH = 'Čestné uznání OSH - MSH'
KSH = 'Čestné uznání KSH - MSH'
SHCMS = 'Čestné uznání SHČMS'
MSF = 'Medaile sv. Floriána'
MZZ = 'Medaile Za zásluhy'
MPP = 'Medaile Za příkladnou práci'
MMZ = 'Medaile Za mimořádné zásluhy'
PS = ['Podmínky splněny']


def test_sweep(make_hasic):
    h = make_hasic()
    for vyz in h.vyznamenani:
        assert isinstance(vyz.podminka(h, YEAR), bool)
        res = vyz.splnene_podminky(h, YEAR)
        assert res
        assert all(isinstance(x, str) for x in res)
        assert repr(vyz) == vyz.nazev
    for vyz in h.vyznamenani:
        vyz.obdrzene = True
        vyz.obdrzene_rok = 2000
    for vyz in h.vyznamenani:
        assert vyz.splnene_podminky(h, YEAR) == ['Obdrženo 2000']
        assert vyz.podminka(h, YEAR) is False


@pytest.mark.parametrize(
    ('attr', 'text'), [
        ('cestne_uznani_okrsku', 'Již se nedává'),
        ('odznak_sv_floriana', 'Již se nedává'),
        ('medaile_za_mezinar_spolupraci1', ''),
        ('medaile_za_mezinar_spolupraci2', ''),
        ('medaile_za_mezinar_spolupraci3', ''),
        ('medaile_za_odvahu_a_statecnost', ''),
        ('medaile_za_zachranu_zivota', ''),
        ('od_jine_organizace', ''),
        ('ostatni_vyznamenani', ''),
        ('pametni_medaile_shcms', ''),
        ('pametni_stuha_shcms', ''),
        ('titul_cestny_clen_shcms', ''),
        ('zasluzny_rad_ceskeho_hasicstva', ''),
    ],
)
def test_simple(make_hasic, attr, text):
    h = make_hasic()
    vyz = getattr(h, attr)
    assert vyz.podminka(h, YEAR) is False
    assert vyz.splnene_podminky(h, YEAR) == [text]
    vyz.obdrzene = True
    vyz.obdrzene_rok = 2010
    assert vyz.podminka(h, YEAR) is False
    assert vyz.splnene_podminky(h, YEAR) == ['Obdrženo 2010']


def test_abstract_bodies(make_hasic):
    h = make_hasic()
    assert Vyznamenani.podminka(h.cestne_uznani_sdh, h, YEAR) is None
    assert Vyznamenani.splnene_podminky(h.cestne_uznani_sdh, h, YEAR) is None


def test_sdh(make_hasic):
    h = make_hasic()
    assert h.cestne_uznani_sdh.podminka(h, YEAR) is True
    assert h.cestne_uznani_sdh.splnene_podminky(h, YEAR) == PS


# attr, awards, narozen, clenem, podminka, splnene
TABLE = [
    ('cestne_uznani_osh', {'cestne_uznani_sdh': 2000}, 1960, 1980, True, PS),
    ('cestne_uznani_osh', {}, 1960, 1980, False, [SDH]),
    (
        'cestne_uznani_ksh',
        {
            'cestne_uznani_sdh': 2000, 'cestne_uznani_osh': 2000,
            'medaile_za_zasluhy': 2000,
        },
        1960, 1980, True, PS,
    ),
    ('cestne_uznani_ksh', {}, 1960, 1980, False, [SDH, OSH, MZZ]),
    (
        'cestne_uznani_ksh',
        {'cestne_uznani_sdh': 2000, 'cestne_uznani_osh': 2000},
        1960, 1980, False, [MZZ],
    ),
    (
        'cestne_uznani_shcms',
        {
            'cestne_uznani_ksh': 2000, 'medaile_sv_floriana': 2000,
            'medaile_za_prikladnou_praci': 2000, 'medaile_za_zasluhy': 2000,
        },
        1960, 1980, True, PS,
    ),
    ('cestne_uznani_shcms', {}, 1960, 1980, False, [KSH, MSF, MPP, MZZ]),
    (
        'cestne_uznani_shcms',
        {
            'cestne_uznani_ksh': 2000, 'medaile_sv_floriana': 2000,
            'medaile_za_prikladnou_praci': 2000,
        },
        1960, 1980, False, [MZZ],
    ),
    ('medaile_sv_floriana', {}, 1960, 1980, False, [KSH, MZZ]),
    (
        'medaile_sv_floriana',
        {'cestne_uznani_ksh': YEAR - 1, 'medaile_za_zasluhy': YEAR - 5},
        1960, 1980, True, PS,
    ),
    (
        'medaile_sv_floriana',
        {'cestne_uznani_ksh': YEAR - 1, 'medaile_za_zasluhy': YEAR - 4},
        1960, 1980, False, [f'{YEAR + 1} (5 let od {MZZ})'],
    ),
    (
        'medaile_sv_floriana', {'cestne_uznani_ksh': YEAR},
        1960, 1980, False, [f'{YEAR + 1} (1 rok od {KSH})', MZZ],
    ),
    (
        'medaile_sv_floriana', {'cestne_uznani_ksh': 2000},
        1960, 1980, False, [MZZ],
    ),
    (
        'medaile_sv_floriana', {'medaile_za_zasluhy': 2000},
        1960, 1980, False, [KSH],
    ),
    (
        'medaile_sv_floriana',
        {'cestne_uznani_ksh': 2000, 'medaile_za_zasluhy': YEAR - 5},
        1960, 1980, True, PS,
    ),
    (
        'medaile_sv_floriana', {'medaile_za_zasluhy': YEAR},
        1960, 1980, False, [KSH, f'{YEAR + 5} (5 let od {MZZ})'],
    ),
    (
        'medaile_za_zasluhy',
        {'cestne_uznani_osh': 2000, 'medaile_za_prikladnou_praci': 2000},
        1960, 1980, True, PS,
    ),
    ('medaile_za_zasluhy', {}, 1960, 1980, False, [OSH, MPP]),
    (
        'medaile_za_zasluhy',
        {'cestne_uznani_osh': 2000, 'medaile_za_prikladnou_praci': YEAR},
        1960, 1980, False, [f'{YEAR + 5} (5 let od {MPP})'],
    ),
    (
        'medaile_za_zasluhy', {'medaile_za_prikladnou_praci': 2000},
        1960, 1980, False, [OSH],
    ),
    (
        'medaile_za_mimoradne_zasluhy',
        {'cestne_uznani_shcms': 2000, 'medaile_sv_floriana': 2000},
        1960, 1980, True, PS,
    ),
    (
        'medaile_za_mimoradne_zasluhy',
        {'cestne_uznani_shcms': 2000, 'odznak_sv_floriana': 2000},
        1960, 1980, True, PS,
    ),
    (
        'medaile_za_mimoradne_zasluhy',
        {'cestne_uznani_shcms': YEAR, 'medaile_sv_floriana': 2000},
        1960, 1980, False, [f'{YEAR + 1} (1 rok od {SHCMS})'],
    ),
    (
        'medaile_za_mimoradne_zasluhy',
        {'cestne_uznani_shcms': YEAR - 1, 'medaile_sv_floriana': YEAR - 5},
        1960, 1980, True, PS,
    ),
    ('medaile_za_mimoradne_zasluhy', {}, 1960, 1980, False, [SHCMS, MSF]),
    (
        'medaile_za_mimoradne_zasluhy', {'medaile_sv_floriana': 2000},
        1960, 1980, False, [SHCMS],
    ),
    (
        'medaile_za_mimoradne_zasluhy',
        {'medaile_sv_floriana': YEAR, 'odznak_sv_floriana': 2000},
        1960, 1980, False, [SHCMS, f'{YEAR + 5} (5 let od {MSF})'],
    ),
    (
        'medaile_za_mimoradne_zasluhy', {'odznak_sv_floriana': 2000},
        1960, 1980, False, [SHCMS],
    ),
    (
        'medaile_za_mimoradne_zasluhy', {'cestne_uznani_shcms': 2000},
        1960, 1980, False, [MSF],
    ),
    (
        'medaile_za_prikladnou_praci', {'cestne_uznani_osh': 2000},
        1960, 1980, True, PS,
    ),
    (
        'medaile_za_prikladnou_praci', {}, 2010, 2020, False,
        [OSH, '2038 (28 let věku)', '2030 (10 let členství)'],
    ),
    (
        'medaile_za_prikladnou_praci', {'cestne_uznani_osh': YEAR},
        1960, 1980, False, [f'{YEAR + 5} (5 let od {OSH})'],
    ),
    (
        'medaile_za_prikladnou_praci', {'cestne_uznani_osh': 2000},
        2010, 1980, False, ['2038 (28 let věku)'],
    ),
    (
        'medaile_za_zasluhy_o_vychovu', {
            'medaile_za_prikladnou_praci': 2000,
        }, 1960, 1980, True, PS,
    ),
    (
        'medaile_za_zasluhy_o_vychovu', {}, 1960, 2020, False,
        [MPP, '2030 (10 let členství a práce s mládeží)'],
    ),
    ('medaile_za_zasluhy_o_vychovu', {}, 1960, 1980, False, [MPP]),
    (
        'medaile_za_zasluhy_o_vychovu', {'medaile_za_prikladnou_praci': 2000},
        1960, 2020, False, ['2030 (10 let členství a práce s mládeží)'],
    ),
    (
        'rad_sv_floriana', {'medaile_za_mimoradne_zasluhy': 2000},
        1970, 1990, True, PS,
    ),
    (
        'rad_sv_floriana', {}, 2010, 2020, False,
        [MMZ, '2060 (50 let věku)', '2050 (30 let členství)'],
    ),
    (
        'rad_sv_floriana', {'medaile_za_mimoradne_zasluhy': YEAR},
        1970, 1990, False, [f'{YEAR + 5} (5 let od {MMZ})'],
    ),
    (
        'rad_sv_floriana', {'medaile_za_mimoradne_zasluhy': 2000},
        1970, 2010, False, ['2040 (30 let členství)'],
    ),
    (
        'rad_sv_floriana', {'medaile_za_mimoradne_zasluhy': 2000},
        1985, 1990, False, ['2035 (50 let věku)'],
    ),
    (
        'rad_sv_floriana', {'medaile_za_mimoradne_zasluhy': YEAR - 5},
        YEAR - 50, YEAR - 30, True, PS,
    ),
    (
        'rad_sv_floriana', {'medaile_za_mimoradne_zasluhy': YEAR - 4},
        YEAR - 49, YEAR - 29, False,
        [
            f'{YEAR + 1} (5 let od {MMZ})', f'{YEAR + 1} (50 let věku)',
            f'{YEAR + 1} (30 let členství)',
        ],
    ),
    (
        'titul_zaslouzily_hasic', {'medaile_za_mimoradne_zasluhy': 2000},
        1950, 1970, True, PS,
    ),
    (
        'titul_zaslouzily_hasic', {}, 2010, 2020, False,
        [MMZ, '2075 (65 let věku)', '2060 (40 let členství)'],
    ),
    (
        'titul_zaslouzily_hasic', {'medaile_za_mimoradne_zasluhy': YEAR},
        1960, 1980, False, [f'{YEAR + 5} (5 let od {MMZ})'],
    ),
    (
        'titul_zaslouzily_hasic', {'medaile_za_mimoradne_zasluhy': 2000},
        2000, 1980, False, ['2065 (65 let věku)'],
    ),
]


@pytest.mark.parametrize(
    ('attr', 'awards', 'narozen', 'clenem', 'podminka', 'splnene'), TABLE,
)
def test_rules(make_hasic, attr, awards, narozen, clenem, podminka, splnene):
    h = make_hasic(narozen, clenem, **awards)
    vyz = getattr(h, attr)
    assert vyz.podminka(h, YEAR) is podminka
    assert vyz.splnene_podminky(h, YEAR) == splnene


@pytest.mark.parametrize(
    ('attr', 'n'),
    [
        ('medaile_za_vernost_10', 10),
        ('stuzka_za_vernost_20', 20),
        ('stuzka_za_vernost_30', 30),
        ('stuzka_za_vernost_40', 40),
        ('stuzka_za_vernost_50', 50),
        ('stuzka_za_vernost_60', 60),
        ('stuzka_za_vernost_70', 70),
        ('stuzka_za_vernost_80', 80),
    ],
)
def test_vernost(make_hasic, attr, n):
    h = make_hasic(clenem=YEAR - n)
    assert getattr(h, attr).podminka(h, YEAR) is True
    assert getattr(h, attr).splnene_podminky(h, YEAR) == PS
    h = make_hasic(clenem=YEAR - n + 1)
    assert getattr(h, attr).podminka(h, YEAR) is False
    assert getattr(h, attr).splnene_podminky(h, YEAR) == [str(YEAR + 1)]


def test_rok_drives_rules(make_hasic):
    h = make_hasic(
        1960, 1980, cestne_uznani_sdh=1990, medaile_za_zasluhy=1995,
    )
    vyz = h.stuzka_za_vernost_30
    assert vyz.podminka(h, 2000) is False
    assert vyz.splnene_podminky(h, 2000) == ['2010']
    assert vyz.podminka(h, 2030) is True
    assert vyz.splnene_podminky(h, 2030) == PS


@pytest.mark.parametrize(
    'ok', list(itertools.product([True, False], repeat=3)),
)
def test_rad_consistency(make_hasic, ok):
    mmz, clenem, narozen = ok
    h = make_hasic(
        YEAR - (50 if narozen else 49),
        YEAR - (30 if clenem else 29),
        medaile_za_mimoradne_zasluhy=YEAR - (5 if mmz else 4),
    )
    vyz = h.rad_sv_floriana
    assert vyz.podminka(h, YEAR) is all(ok)
    res = vyz.splnene_podminky(h, YEAR)
    assert (res == PS) is all(ok)
    if not clenem:
        assert '(30 let členství)' in ' '.join(res)


def aw(attr, n=0):
    return ('aw', attr, n)


def age(n):
    return ('age', None, n)


def mem(n):
    return ('mem', None, n)


# award -> prerequisites, each a tuple of alternatives (any one is enough)
RULES = {
    'cestne_uznani_osh': [(aw('cestne_uznani_sdh'),)],
    'cestne_uznani_ksh': [
        (aw('cestne_uznani_sdh'),), (aw('cestne_uznani_osh'),),
        (aw('medaile_za_zasluhy'),),
    ],
    'cestne_uznani_shcms': [
        (aw('cestne_uznani_ksh'),), (aw('medaile_sv_floriana'),),
        (aw('medaile_za_prikladnou_praci'),), (aw('medaile_za_zasluhy'),),
    ],
    'medaile_sv_floriana': [
        (aw('cestne_uznani_ksh', 1),), (aw('medaile_za_zasluhy', 5),),
    ],
    'medaile_za_zasluhy': [
        (aw('cestne_uznani_osh'),), (aw('medaile_za_prikladnou_praci', 5),),
    ],
    'medaile_za_mimoradne_zasluhy': [
        (aw('cestne_uznani_shcms', 1),),
        (aw('medaile_sv_floriana', 5), aw('odznak_sv_floriana', 5)),
    ],
    'medaile_za_prikladnou_praci': [
        (aw('cestne_uznani_osh', 5),), (age(28),), (mem(10),),
    ],
    'medaile_za_zasluhy_o_vychovu': [
        (aw('medaile_za_prikladnou_praci'),), (mem(10),),
    ],
    'rad_sv_floriana': [
        (aw('medaile_za_mimoradne_zasluhy', 5),), (age(50),), (mem(30),),
    ],
    'titul_zaslouzily_hasic': [
        (aw('medaile_za_mimoradne_zasluhy', 5),), (age(65),), (mem(40),),
    ],
    **{
        f'{attr}_{n}': [(mem(n),)] for attr, n in [
            ('medaile_za_vernost', 10), ('stuzka_za_vernost', 20),
            ('stuzka_za_vernost', 30), ('stuzka_za_vernost', 40),
            ('stuzka_za_vernost', 50), ('stuzka_za_vernost', 60),
            ('stuzka_za_vernost', 70), ('stuzka_za_vernost', 80),
        ]
    },
}


def states(cond):
    kind, _, n = cond
    deltas = (-1, 0, 1) if n or kind != 'aw' else (0,)
    # None = prerequisite award not obtained
    return [None, *deltas] if kind == 'aw' else list(deltas)


@pytest.mark.parametrize('attr', RULES)
def test_podminka_matches_splnene(make_hasic, attr):
    conds = [c for alts in RULES[attr] for c in alts]
    for combo in itertools.product(*(states(c) for c in conds)):
        d = dict(zip(conds, combo))
        awards, narozen, clenem = {}, 1960, 1980
        for (kind, name, n), delta in d.items():
            if kind == 'aw' and delta is not None:
                awards[name] = YEAR - n - delta
            elif kind == 'age':
                narozen = YEAR - n - delta
            elif kind == 'mem':
                clenem = YEAR - n - delta
        h = make_hasic(narozen, clenem, **awards)
        expected = all(
            any(d[c] is not None and d[c] >= 0 for c in alts)
            for alts in RULES[attr]
        )
        vyz = getattr(h, attr)
        assert vyz.podminka(h, YEAR) is expected, d
        assert (vyz.splnene_podminky(h, YEAR) == PS) is expected, d
