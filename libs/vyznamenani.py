from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from libs.hasic import Hasic


class Vyznamenani(ABC):
    def __init__(self, nazev: str) -> None:
        self.nazev: str = nazev
        self.obdrzene: bool = False
        self.obdrzene_rok: int = 0

    def __repr__(self):
        return self.nazev

    @abstractmethod
    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        pass

    @abstractmethod
    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        pass


class Cestne_uznani_sdh(Vyznamenani):
    def __init__(self):
        super().__init__('Čestné uznání SDH')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if not self.obdrzene:
            return True
        else:
            return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['Podmínky splněny']


class Cestne_uznani_osh(Vyznamenani):
    def __init__(self):
        super().__init__('Čestné uznání OSH - MSH')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if hasic.cestne_uznani_sdh.obdrzene and not self.obdrzene:
            return True
        else:
            return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if hasic.cestne_uznani_sdh.obdrzene:
            return ['Podmínky splněny']
        else:
            return [hasic.cestne_uznani_sdh.nazev]


class Cestne_uznani_ksh(Vyznamenani):
    def __init__(self):
        super().__init__('Čestné uznání KSH - MSH')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            hasic.cestne_uznani_sdh.obdrzene and
            hasic.cestne_uznani_osh.obdrzene and
            hasic.medaile_za_zasluhy.obdrzene and
            not self.obdrzene
        ):
            return True
        else:
            return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if (
            hasic.cestne_uznani_sdh.obdrzene and
            hasic.cestne_uznani_osh.obdrzene and
            hasic.medaile_za_zasluhy.obdrzene
        ):
            return ['Podmínky splněny']
        else:
            vysledek = []
            if not hasic.cestne_uznani_sdh.obdrzene:
                vysledek.append(hasic.cestne_uznani_sdh.nazev)
            if not hasic.cestne_uznani_osh.obdrzene:
                vysledek.append(hasic.cestne_uznani_osh.nazev)
            if not hasic.medaile_za_zasluhy.obdrzene:
                vysledek.append(hasic.medaile_za_zasluhy.nazev)
            return vysledek
        return ['Chyba']


class Cestne_uznani_okrsku(Vyznamenani):
    def __init__(self):
        super().__init__('Čestné uznání okrsku')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['Již se nedává']


class Cestne_uznani_shcms(Vyznamenani):
    def __init__(self):
        super().__init__('Čestné uznání SHČMS')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            hasic.cestne_uznani_ksh.obdrzene and
            hasic.medaile_sv_floriana.obdrzene and
            hasic.medaile_za_prikladnou_praci.obdrzene and
            hasic.medaile_za_zasluhy.obdrzene and
            not self.obdrzene
        ):
            return True
        else:
            return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if (
            hasic.cestne_uznani_ksh.obdrzene and
            hasic.medaile_sv_floriana.obdrzene and
            hasic.medaile_za_prikladnou_praci.obdrzene and
            hasic.medaile_za_zasluhy.obdrzene
        ):
            return ['Podmínky splněny']
        else:
            vysledek = []
            if not hasic.cestne_uznani_ksh.obdrzene:
                vysledek.append(hasic.cestne_uznani_ksh.nazev)
            if not hasic.medaile_sv_floriana.obdrzene:
                vysledek.append(hasic.medaile_sv_floriana.nazev)
            if not hasic.medaile_za_prikladnou_praci.obdrzene:
                vysledek.append(hasic.medaile_za_prikladnou_praci.nazev)
            if not hasic.medaile_za_zasluhy.obdrzene:
                vysledek.append(hasic.medaile_za_zasluhy.nazev)
            return vysledek
        return ['Chyba']


class Medaile_sv_floriana(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile sv. Floriána')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            hasic.cestne_uznani_ksh.obdrzene and
            not self.obdrzene
        ):
            if rok - hasic.cestne_uznani_ksh.obdrzene_rok >= 1:
                if (
                    hasic.medaile_za_zasluhy.obdrzene and
                    rok - hasic.medaile_za_zasluhy.obdrzene_rok >= 5
                ):
                    return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if (
            hasic.medaile_za_zasluhy.obdrzene and
            rok - hasic.medaile_za_zasluhy.obdrzene_rok >= 5
        ):
            return ['Podmínky splněny']
        else:
            vysledek = []
            if not hasic.medaile_za_zasluhy.obdrzene:
                vysledek.append(hasic.medaile_za_zasluhy.nazev)
            elif not rok - hasic.medaile_za_zasluhy.obdrzene_rok >= 5:
                vysledek.append(
                    f'{hasic.medaile_za_zasluhy.obdrzene_rok + 5} ' +
                    f'(5 let od {hasic.medaile_za_zasluhy.nazev})',
                )
            return vysledek
        return ['Chyba']


class Medaile_za_mezinar_spolupraci1(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za mezinárodní spolupráci I. stupně')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Medaile_za_mezinar_spolupraci2(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za mezinárodní spolupráci II. stupně')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Medaile_za_mezinar_spolupraci3(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za mezinárodní spolupráci IIIs. stupně')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Medaile_za_zasluhy(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za zásluhy')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            hasic.cestne_uznani_osh.obdrzene and
            hasic.medaile_za_prikladnou_praci.obdrzene and
            rok - hasic.medaile_za_prikladnou_praci.obdrzene_rok >= 5 and
            not self.obdrzene
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if (
            hasic.cestne_uznani_osh.obdrzene and
            hasic.medaile_za_prikladnou_praci.obdrzene and
            rok - hasic.medaile_za_prikladnou_praci.obdrzene_rok >= 5
        ):
            return ['Podmínky splněny']
        else:
            vysledek = []
            if not hasic.cestne_uznani_osh.obdrzene:
                vysledek.append(hasic.cestne_uznani_osh.nazev)
            if not hasic.medaile_za_prikladnou_praci.obdrzene:
                vysledek.append(hasic.medaile_za_prikladnou_praci.nazev)
            elif not rok - hasic.medaile_za_prikladnou_praci.obdrzene_rok >= 5:
                vysledek.append(
                    f'{hasic.medaile_za_prikladnou_praci.obdrzene_rok + 5} ' +
                    f'(5 let od {hasic.medaile_za_prikladnou_praci.nazev})',
                )
            return vysledek
        return ['Chyba']


class Medaile_za_mimoradne_zasluhy(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za mimořádné zásluhy')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            hasic.cestne_uznani_shcms.obdrzene and
            rok - hasic.cestne_uznani_shcms.obdrzene_rok >= 1 and
            (
                (
                    hasic.medaile_sv_floriana.obdrzene and
                    rok - hasic.medaile_sv_floriana.obdrzene_rok >= 5
                )
                or
                (
                    hasic.odznak_sv_floriana.obdrzene and
                    rok - hasic.odznak_sv_floriana.obdrzene_rok >= 5
                )
            )
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if (
            hasic.cestne_uznani_shcms.obdrzene and
            (
                (
                    hasic.medaile_sv_floriana.obdrzene and
                    rok - hasic.medaile_sv_floriana.obdrzene_rok >= 5
                )
                or
                (
                    hasic.odznak_sv_floriana.obdrzene and
                    rok - hasic.odznak_sv_floriana.obdrzene_rok >= 5
                )
            )
        ):
            return ['Podmínky splněny']
        else:
            vysledek = []
            if not hasic.cestne_uznani_shcms.obdrzene:
                vysledek.append(hasic.cestne_uznani_shcms.nazev)
            if not (
                (
                    hasic.medaile_sv_floriana.obdrzene and
                    rok - hasic.medaile_sv_floriana.obdrzene_rok >= 5
                )
                or
                (
                    hasic.odznak_sv_floriana.obdrzene and
                    rok - hasic.odznak_sv_floriana.obdrzene_rok >= 5
                )
            ):
                vysledek.append(hasic.medaile_sv_floriana.nazev)
            elif not rok - hasic.medaile_sv_floriana.obdrzene_rok >= 5:
                vysledek.append(
                    f'{hasic.medaile_sv_floriana.obdrzene_rok + 5} ' +
                    f'(5 let od {hasic.medaile_sv_floriana.nazev})',
                )
            return vysledek
        return ['Chyba']


class Medaile_za_odvahu_a_statecnost(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za odvahu a statečnost')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Medaile_za_prikladnou_praci(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za příkladnou práci')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            hasic.cestne_uznani_osh.obdrzene and
            rok - hasic.cestne_uznani_osh.obdrzene_rok >= 5 and
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 10 and
            rok - int(hasic.datum_narozeni[-4:]) >= 28
        ):
            return True
        else:
            return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if (
            hasic.cestne_uznani_osh.obdrzene and
            rok - hasic.cestne_uznani_osh.obdrzene_rok >= 5 and
            rok - int(hasic.clenem_od[-4:]) >= 10 and
            rok - int(hasic.datum_narozeni[-4:]) >= 28
        ):
            return ['Podmínky splněny']
        else:
            vysledek = []
            if not hasic.cestne_uznani_osh.obdrzene:
                vysledek.append(hasic.cestne_uznani_osh.nazev)
            elif not rok - hasic.cestne_uznani_osh.obdrzene_rok >= 5:
                vysledek.append(
                    f'{hasic.cestne_uznani_osh.obdrzene_rok + 5} ' +
                    f'(5 let od {hasic.cestne_uznani_osh.nazev})',
                )
            if not rok - int(hasic.datum_narozeni[-4:]) >= 28:
                vysledek.append(
                    f'{int(hasic.datum_narozeni[-4:]) + 28} (28 let věku)',
                )
            if not rok - int(hasic.clenem_od[-4:]) >= 10:
                vysledek.append(
                    f'{int(hasic.clenem_od[-4:]) + 10} (10 let členství)',
                )
            return vysledek
        return ['Chyba']


class Medaile_za_zachranu_zivota(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za záchranu života')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Medaile_za_zasluhy_o_vychovu(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za zásluhy o výchovu')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            hasic.medaile_za_prikladnou_praci.obdrzene and
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 10
        ):
            return True
        else:
            return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if (
            hasic.medaile_za_prikladnou_praci.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 10
        ):
            return ['Podmínky splněny']
        else:
            vysledek = []
            if not hasic.medaile_za_prikladnou_praci.obdrzene:
                vysledek.append(hasic.medaile_za_prikladnou_praci.nazev)
            if not rok - int(hasic.clenem_od[-4:]) >= 10:
                vysledek.append(
                    f'{int(hasic.clenem_od[-4:]) + 10}' +
                    '(10 let členství a práce s mládeží)',
                )
            return vysledek
        return ['Chyba']


class Od_jine_organizace(Vyznamenani):
    def __init__(self):
        super().__init__('Od jiné organizace')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Odznak_sv_floriana(Vyznamenani):
    def __init__(self):
        super().__init__('Odznak sv. Floriána')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['Již se nedává']


class Ostatni_vyznamenani(Vyznamenani):
    def __init__(self):
        super().__init__('Ostatní vyznamenání')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Pametni_medaile_shcms(Vyznamenani):
    def __init__(self):
        super().__init__('Pamětní medaile organizačních jednotek SH ČMS')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Pametni_stuha_shcms(Vyznamenani):
    def __init__(self):
        super().__init__('Pamětní stuha organizačních jednotek SH ČMS')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Rad_sv_floriana(Vyznamenani):
    def __init__(self):
        super().__init__('Řád sv. Floriána')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            hasic.medaile_za_mimoradne_zasluhy.obdrzene and
            rok - hasic.medaile_za_mimoradne_zasluhy.obdrzene_rok >= 5 and
            rok - int(hasic.clenem_od[-4:]) >= 30 and
            rok - int(hasic.datum_narozeni[-4:]) >= 50
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if (
            hasic.medaile_za_mimoradne_zasluhy.obdrzene and
            rok - hasic.medaile_za_mimoradne_zasluhy.obdrzene_rok >= 5 and
            rok - int(hasic.clenem_od[-4:]) >= 30 and
            rok - int(hasic.datum_narozeni[-4:]) >= 28
        ):
            return ['Podmínky splněny']
        else:
            vysledek = []
            if not hasic.medaile_za_mimoradne_zasluhy.obdrzene:
                vysledek.append(hasic.medaile_za_mimoradne_zasluhy.nazev)
            elif (
                not rok - hasic.medaile_za_mimoradne_zasluhy.obdrzene_rok >= 5
            ):
                vysledek.append(
                    f'{hasic.medaile_za_mimoradne_zasluhy.obdrzene_rok + 5} ' +
                    f'(5 let od {hasic.medaile_za_mimoradne_zasluhy.nazev})',
                )
            if not rok - int(hasic.datum_narozeni[-4:]) >= 28:
                vysledek.append(
                    f'{int(hasic.datum_narozeni[-4:]) + 28} (28 let věku)',
                )
            if not rok - int(hasic.clenem_od[-4:]) >= 30:
                vysledek.append(
                    f'{int(hasic.clenem_od[-4:]) + 30} (10 let členství)',
                )
            return vysledek
        return ['Chyba']


class Medaile_za_vernost_10(Vyznamenani):
    def __init__(self):
        super().__init__('Medaile Za věrnost 10 let')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 10
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if rok - int(hasic.clenem_od[-4:]) >= 10:
            return ['Podmínky splněny']
        return [str(int(hasic.clenem_od[-4:]) + 10)]


class Stuzka_za_vernost_20(Vyznamenani):
    def __init__(self):
        super().__init__('Stužka za věrnost 20 let')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 20
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if rok - int(hasic.clenem_od[-4:]) >= 20:
            return ['Podmínky splněny']
        return [str(int(hasic.clenem_od[-4:]) + 20)]


class Stuzka_za_vernost_30(Vyznamenani):
    def __init__(self):
        super().__init__('Stužka za věrnost 30 let')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 30
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if rok - int(hasic.clenem_od[-4:]) >= 30:
            return ['Podmínky splněny']
        return [str(int(hasic.clenem_od[-4:]) + 30)]


class Stuzka_za_vernost_40(Vyznamenani):
    def __init__(self):
        super().__init__('Stužka za věrnost 40 let')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 40
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if rok - int(hasic.clenem_od[-4:]) >= 40:
            return ['Podmínky splněny']
        return [str(int(hasic.clenem_od[-4:]) + 40)]


class Stuzka_za_vernost_50(Vyznamenani):
    def __init__(self):
        super().__init__('Stužka za věrnost 50 let')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 50
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if rok - int(hasic.clenem_od[-4:]) >= 50:
            return ['Podmínky splněny']
        return [str(int(hasic.clenem_od[-4:]) + 50)]


class Stuzka_za_vernost_60(Vyznamenani):
    def __init__(self):
        super().__init__('Stužka za věrnost 60 let')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 60
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if rok - int(hasic.clenem_od[-4:]) >= 60:
            return ['Podmínky splněny']
        return [str(int(hasic.clenem_od[-4:]) + 60)]


class Stuzka_za_vernost_70(Vyznamenani):
    def __init__(self):
        super().__init__('Stužka za věrnost 70 let')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 70
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if rok - int(hasic.clenem_od[-4:]) >= 70:
            return ['Podmínky splněny']
        return [str(int(hasic.clenem_od[-4:]) + 70)]


class Stuzka_za_vernost_80(Vyznamenani):
    def __init__(self):
        super().__init__('Stužka za věrnost 80 let')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            not self.obdrzene and
            rok - int(hasic.clenem_od[-4:]) >= 80
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if rok - int(hasic.clenem_od[-4:]) >= 80:
            return ['Podmínky splněny']
        return [str(int(hasic.clenem_od[-4:]) + 80)]


class Titul_cestny_clen_shcms(Vyznamenani):
    def __init__(self):
        super().__init__('Titul Čestný člen  SH ČMS')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']


class Titul_zaslouzily_hasic(Vyznamenani):
    def __init__(self):
        super().__init__('Titul Zasloužilý hasič')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        if (
            hasic.medaile_za_mimoradne_zasluhy.obdrzene and
            rok - hasic.medaile_za_mimoradne_zasluhy.obdrzene_rok >= 5 and
            rok - int(hasic.datum_narozeni[-4:]) >= 65 and
            rok - int(hasic.clenem_od[-4:]) >= 40
        ):
            return True
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        rok = datetime.now().year
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        if (
            hasic.medaile_za_mimoradne_zasluhy.obdrzene and
            rok - hasic.medaile_za_mimoradne_zasluhy.obdrzene_rok >= 5 and
            rok - int(hasic.datum_narozeni[-4:]) >= 65 and
            rok - int(hasic.clenem_od[-4:]) >= 40
        ):
            return ['Podmínky splněny']
        else:
            vysledek = []
            if not hasic.medaile_za_mimoradne_zasluhy.obdrzene:
                vysledek.append(hasic.medaile_za_mimoradne_zasluhy.nazev)
            elif (
                not rok - hasic.medaile_za_mimoradne_zasluhy.obdrzene_rok >= 5
            ):
                vysledek.append(
                    f'{hasic.medaile_za_mimoradne_zasluhy.obdrzene_rok + 5} ' +
                    f'(5 let od {hasic.medaile_za_mimoradne_zasluhy.nazev})',
                )
            if not rok - int(hasic.datum_narozeni[-4:]) >= 65:
                vysledek.append(
                    f'{int(hasic.datum_narozeni[-4:]) + 65} (65 let věku)',
                )
            if not rok - int(hasic.clenem_od[-4:]) >= 40:
                vysledek.append(
                    f'{int(hasic.clenem_od[-4:]) + 40} (40 let členství)',
                )
            return vysledek
        return ['Chyba']


class Zasluzny_rad_ceskeho_hasicstva(Vyznamenani):
    def __init__(self):
        super().__init__('Záslužný Řád českého hasičstva')

    def podminka(self, hasic: 'Hasic', rok: int) -> bool:
        return False

    def splnene_podminky(self, hasic: 'Hasic') -> list[str]:
        if self.obdrzene:
            return [f'Obdrženo {self.obdrzene_rok}']
        return ['']
