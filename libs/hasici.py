from pprint import pprint

from libs.hasic import Hasic


class Hasici:
    def __init__(self) -> None:
        self.hasici: list[Hasic] = []
        self.retezce = {
            'datum_narozeni': 'Datum narození',
            'vek': 'Věk',
            'clenem_od': 'Členem SHČMS od',
            'cestne_uznani_sdh': 'Čestné uznání SDH',
            'cestne_uznani_osh': 'Čestné uznání OSH - MSH',
            'cestne_uznani_okrsku': 'Čestné uznání okrsku',
            'cestne_uznani_ksh': 'Čestné uznání KSH - MSH',
            'cestne_uznani_shcms': 'Čestné uznání SHČMS',
            'medaile_sv_floriana': 'Medaile sv. Floriána',
            'medaile_za_mezinar_spolupraci1':
                'Medaile Za mezinárodní spolupráci I. stupně',
            'medaile_za_mezinar_spolupraci2':
                'Medaile Za mezinárodní spolupráci II. stupně',
            'medaile_za_mezinar_spolupraci3':
                'Medaile Za mezinárodní spolupráci III. stupně',
            'medaile_za_zasluhy': 'Medaile Za zásluhy',
            'medaile_za_mimoradne_zasluhy': 'Medaile Za mimořádné zásluhy',
            'medaile_za_odvahu_a_statecnost': 'Medaile Za odvahu a statečnost',
            'medaile_za_prikladnou_praci': 'Medaile Za příkladnou práci',
            'medaile_za_zachranu_zivota': 'Medaile Za záchranu života',
            'medaile_za_zasluhy_o_vychovu': 'Medaile Za zásluhy o výchovu',
            'od_jine_organizace': 'Od jiné organizace',
            'odznak_sv_floriana': 'Odznak sv. Floriána',
            'ostatni_vyznamenani': 'Ostatní vyznamenání',
            'pametni_medaile_shcms':
                'Pamětní medaile organizačních jednotek SH ČMS',
            'pametni_stuha_shcms':
                'Pamětní stuha organizačních jednotek SH ČMS',
            'rad_sv_floriana': 'Řád sv. Floriána',
            'medaile_za_vernost_10': 'Medaile Za věrnost 10 let',
            'stuzka_za_vernost_20': 'Stužka za věrnost 20 let',
            'stuzka_za_vernost_30': 'Stužka za věrnost 30 let',
            'stuzka_za_vernost_40': 'Stužka za věrnost 40 let',
            'stuzka_za_vernost_50': 'Stužka za věrnost 50 let',
            'stuzka_za_vernost_60': 'Stužka za věrnost 60 let',
            'stuzka_za_vernost_70': 'Stužka za věrnost 70 let',
            'stuzka_za_vernost_80': 'Stužka za věrnost 80 let',
            'titul_cestny_clen_shcms': 'Titul Čestný člen  SH ČMS',
            'titul_zaslouzily_hasic': 'Titul Zasloužilý hasič',
            'zasluzny_rad_ceskeho_hasicstva': 'Záslužný Řád českého hasičstva',
        }

    def create_hasici_from_export(self, lines: list[str]) -> None:
        _novy_hasic = Hasic()
        for i, line in enumerate(lines):
            if not i + 1 >= len(lines):
                # ziskat jmeno
                if '==========================' in lines[i + 1][0]:
                    if _novy_hasic.jmeno:
                        self.hasici.append(_novy_hasic)
                        _novy_hasic = Hasic()
                    _novy_hasic.jmeno = ' '.join(line)
                # ziskat dalsi informace
                elif line[0] == '-':  # radky zacinajici pomlckou
                    if 'Členem SHČMS od' in ' '.join(line):
                        _novy_hasic.clenem_od = line[1][:-1]
                    if 'Datum narození' in ' '.join(line):
                        _novy_hasic.datum_narozeni = line[1][:-1]
                    if line[2] == 'Věk':
                        _novy_hasic.vek = int(line[1][:-1])
                    for vyz in _novy_hasic.vyznamenani:
                        llen = len(vyz.nazev.split())
                        if ' '.join(line[-llen:]) == vyz.nazev:
                            vyz.obdrzene = True
                            obdrzene_str = ' '.join(line[:-llen])[2:][:-1]
                            if ',' in obdrzene_str:
                                obdrzene_rok = int(
                                    obdrzene_str.split(',')[-1].strip(),
                                )
                            else:
                                obdrzene_rok = int(obdrzene_str)
                            vyz.obdrzene_rok = obdrzene_rok
                        else:
                            pass
        self.hasici.append(_novy_hasic)

    def print_all(self) -> None:
        print('hasici a jiz ziskane vyznamenani:')
        for hasic in self.hasici:
            print(hasic)
        print('=' * 30)

    def print_splnene_podminky_all(self, rok: int) -> None:
        print('Splněné podmínky:')
        print('-' * 20)
        for hasic in self.hasici:
            print(hasic.jmeno, hasic.datum_narozeni[-4:])
            for vyz in hasic.vyznamenani:
                if vyz.podminka(hasic, rok):
                    print(vyz.nazev)
            print('-' * 20)

    def print_splnene_podminky(self) -> None:
        print('Splnene podminky:')
        for hasic in self.hasici:
            print(hasic.jmeno)
            for vyz in hasic.vyznamenani:
                pprint([vyz.nazev, vyz.splnene_podminky(hasic)])
            print('-'*30)
