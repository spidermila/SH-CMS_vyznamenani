from datetime import datetime

from libs.vyznamenani import Cestne_uznani_ksh
from libs.vyznamenani import Cestne_uznani_okrsku
from libs.vyznamenani import Cestne_uznani_osh
from libs.vyznamenani import Cestne_uznani_sdh
from libs.vyznamenani import Cestne_uznani_shcms
from libs.vyznamenani import Medaile_sv_floriana
from libs.vyznamenani import Medaile_za_mezinar_spolupraci1
from libs.vyznamenani import Medaile_za_mezinar_spolupraci2
from libs.vyznamenani import Medaile_za_mezinar_spolupraci3
from libs.vyznamenani import Medaile_za_mimoradne_zasluhy
from libs.vyznamenani import Medaile_za_odvahu_a_statecnost
from libs.vyznamenani import Medaile_za_prikladnou_praci
from libs.vyznamenani import Medaile_za_vernost_10
from libs.vyznamenani import Medaile_za_zachranu_zivota
from libs.vyznamenani import Medaile_za_zasluhy
from libs.vyznamenani import Medaile_za_zasluhy_o_vychovu
from libs.vyznamenani import Od_jine_organizace
from libs.vyznamenani import Odznak_sv_floriana
from libs.vyznamenani import Ostatni_vyznamenani
from libs.vyznamenani import Pametni_medaile_shcms
from libs.vyznamenani import Pametni_stuha_shcms
from libs.vyznamenani import Rad_sv_floriana
from libs.vyznamenani import Stuzka_za_vernost_20
from libs.vyznamenani import Stuzka_za_vernost_30
from libs.vyznamenani import Stuzka_za_vernost_40
from libs.vyznamenani import Stuzka_za_vernost_50
from libs.vyznamenani import Stuzka_za_vernost_60
from libs.vyznamenani import Stuzka_za_vernost_70
from libs.vyznamenani import Stuzka_za_vernost_80
from libs.vyznamenani import Titul_cestny_clen_shcms
from libs.vyznamenani import Titul_zaslouzily_hasic
from libs.vyznamenani import Vyznamenani
from libs.vyznamenani import Zasluzny_rad_ceskeho_hasicstva


class Hasic:
    def __init__(self):
        self.now = datetime.now()
        self.jmeno: str = ''
        self.datum_narozeni: str = ''
        self.vek: int = 0
        self.clenem_od: str = ''
        self.vyznamenani: list[Vyznamenani] = []
        self.cestne_uznani_sdh = Cestne_uznani_sdh()
        self.cestne_uznani_osh = Cestne_uznani_osh()
        self.cestne_uznani_ksh = Cestne_uznani_ksh()
        self.cestne_uznani_shcms = Cestne_uznani_shcms()
        self.medaile_sv_floriana = Medaile_sv_floriana()
        self.medaile_za_zasluhy = Medaile_za_zasluhy()
        self.medaile_za_mimoradne_zasluhy = Medaile_za_mimoradne_zasluhy()
        self.medaile_za_prikladnou_praci = Medaile_za_prikladnou_praci()
        self.medaile_za_zasluhy_o_vychovu = Medaile_za_zasluhy_o_vychovu()
        self.rad_sv_floriana = Rad_sv_floriana()
        self.medaile_za_vernost_10 = Medaile_za_vernost_10()
        self.stuzka_za_vernost_20 = Stuzka_za_vernost_20()
        self.stuzka_za_vernost_30 = Stuzka_za_vernost_30()
        self.stuzka_za_vernost_40 = Stuzka_za_vernost_40()
        self.stuzka_za_vernost_50 = Stuzka_za_vernost_50()
        self.stuzka_za_vernost_60 = Stuzka_za_vernost_60()
        self.stuzka_za_vernost_70 = Stuzka_za_vernost_70()
        self.stuzka_za_vernost_80 = Stuzka_za_vernost_80()
        self.titul_zaslouzily_hasic = Titul_zaslouzily_hasic()
        self.titul_cestny_clen_shcms = Titul_cestny_clen_shcms()
        self.od_jine_organizace = Od_jine_organizace()
        self.ostatni_vyznamenani = Ostatni_vyznamenani()
        self.pametni_medaile_shcms = Pametni_medaile_shcms()
        self.pametni_stuha_shcms = Pametni_stuha_shcms()
        self.medaile_za_zachranu_zivota = Medaile_za_zachranu_zivota()
        self.medaile_za_odvahu_a_statecnost = Medaile_za_odvahu_a_statecnost()
        self.medaile_za_mezinar_spolupraci1 = Medaile_za_mezinar_spolupraci1()
        self.medaile_za_mezinar_spolupraci2 = Medaile_za_mezinar_spolupraci2()
        self.medaile_za_mezinar_spolupraci3 = Medaile_za_mezinar_spolupraci3()
        self.zasluzny_rad_ceskeho_hasicstva = Zasluzny_rad_ceskeho_hasicstva()
        self.cestne_uznani_okrsku = Cestne_uznani_okrsku()
        self.odznak_sv_floriana = Odznak_sv_floriana()

        self.vyznamenani.append(self.cestne_uznani_sdh)
        self.vyznamenani.append(self.cestne_uznani_osh)
        self.vyznamenani.append(self.cestne_uznani_ksh)
        self.vyznamenani.append(self.cestne_uznani_shcms)
        self.vyznamenani.append(self.medaile_sv_floriana)
        self.vyznamenani.append(self.medaile_za_zasluhy)
        self.vyznamenani.append(self.medaile_za_mimoradne_zasluhy)
        self.vyznamenani.append(self.medaile_za_prikladnou_praci)
        self.vyznamenani.append(self.medaile_za_zasluhy_o_vychovu)
        self.vyznamenani.append(self.rad_sv_floriana)
        self.vyznamenani.append(self.medaile_za_vernost_10)
        self.vyznamenani.append(self.stuzka_za_vernost_20)
        self.vyznamenani.append(self.stuzka_za_vernost_30)
        self.vyznamenani.append(self.stuzka_za_vernost_40)
        self.vyznamenani.append(self.stuzka_za_vernost_50)
        self.vyznamenani.append(self.stuzka_za_vernost_60)
        self.vyznamenani.append(self.stuzka_za_vernost_70)
        self.vyznamenani.append(self.stuzka_za_vernost_80)
        self.vyznamenani.append(self.titul_zaslouzily_hasic)
        self.vyznamenani.append(self.titul_cestny_clen_shcms)
        self.vyznamenani.append(self.od_jine_organizace)
        self.vyznamenani.append(self.ostatni_vyznamenani)
        self.vyznamenani.append(self.pametni_medaile_shcms)
        self.vyznamenani.append(self.pametni_stuha_shcms)
        self.vyznamenani.append(self.medaile_za_zachranu_zivota)
        self.vyznamenani.append(self.medaile_za_odvahu_a_statecnost)
        self.vyznamenani.append(self.medaile_za_mezinar_spolupraci1)
        self.vyznamenani.append(self.medaile_za_mezinar_spolupraci2)
        self.vyznamenani.append(self.medaile_za_mezinar_spolupraci3)
        self.vyznamenani.append(self.zasluzny_rad_ceskeho_hasicstva)
        self.vyznamenani.append(self.cestne_uznani_okrsku)
        self.vyznamenani.append(self.odznak_sv_floriana)

    def __repr__(self):
        result = \
            f'{self.jmeno}\n' +\
            f'{self.datum_narozeni}\n' +\
            f'{self.vek} let\n' +\
            f'clenem od {self.clenem_od}\n'
        for vyz in self.vyznamenani:
            if vyz.obdrzene:
                result += f'{vyz.nazev} - {vyz.obdrzene_rok} \n'
        return result

    def get_owned_vyznamenani(self) -> list[dict[str, int]]:
        vysledek = []
        for vyz in self.vyznamenani:
            if vyz.obdrzene:
                vysledek.append({vyz.nazev: vyz.obdrzene_rok})
        return vysledek

    def get_splnene_podminky(self, rok: int) -> list[str]:
        sps = []
        for vyz in [x for x in self.vyznamenani if not x.obdrzene]:
            if vyz.podminka(self, rok):
                sps.append(vyz.nazev)
        return sps
