# SH-CMS_vyznamenani
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/spidermila/SH-CMS_vyznamenani/main.svg)](https://results.pre-commit.ci/latest/github/spidermila/SH-CMS_vyznamenani/main)

### Program pro vytvoření přehledu vyznamenání členů SDH SH-ČMS.
Toto byl můj malý projekt pro ulehčení práce ve výboru SDH. Myslím, že by se mohl ale hodit i jiným SDH, tak jsem se rozhodl program zveřejnit.

## Webová verze (doporučeno)
Hlavním rozhraním programu je webová aplikace. Po zadání přihlašovacích údajů k evidencesdh.cz a 2FA kódu se aplikace sama přihlásí, stáhne export členů vašeho SDH a vrátí hotovou tabulku MS Excel ke stažení. Export tak není nutné stahovat ručně.

Výsledkem je tabulka, která slouží jako přehled již získaných vyznamenání a také ukazuje podmínky pro získání vyznamenání, které ještě nebyly obdrženy.
![ukázka výsledku](https://github.com/spidermila/SH-CMS_vyznamenani/blob/main/tabulka.png)

### Provoz webové aplikace
Aplikace běží v Dockeru:
```bash
git clone https://github.com/spidermila/SH-CMS_vyznamenani.git
cd SH-CMS_vyznamenani
cp .env_sample .env
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # výsledek vložte do .env jako APP_SECRET_KEY
docker compose up -d --build
```
Aplikace pak běží na portu 5556, např. http://localhost:5556/

## Příkazová řádka
Program lze stále spustit i z příkazové řádky nad ručně staženým exportem. Vstupem je textový soubor s exportem členů vašeho SDH, který může oprávněná osoba získat na webu evidencesdh.cz - viz obrázek níže:
![ukázka evidencesdh.cz](https://github.com/spidermila/SH-CMS_vyznamenani/blob/main/evidencesdh.png)

Vyžaduje Python 3.11 nebo novější.
```bash
git clone https://github.com/spidermila/SH-CMS_vyznamenani.git
cd SH-CMS_vyznamenani
python3 -m venv venv               # Windows: py -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python SH-CMS_vyznamenani.py muj_export.txt -o muj_vystup.xlsx
```

Parametry:
- `soubor` - textový export z evidencesdh.cz
- `-o, --output` - název výstupního souboru, musí mít příponu `.xlsx` (velikost písmen nerozhoduje), výchozí je `test.xlsx`
- `-r, --rok` - rok, ke kterému se kontrolují podmínky, výchozí je aktuální rok, např. `-r 2030`
- `-h, --help` - zobrazí nápovědu

## Vývoj a testy
```bash
pip install -r requirements-dev.txt
pytest                          # spustí testy a vyžaduje 100% pokrytí kódu
pip install pre-commit
pre-commit run --all-files
```

## Připomínky, nápady
Pokud narazíte na problém s programem, nebo budete mít nápad na vylepšení, pošlete mi zprávu, nebo vytvořte Issue.

Případně můžete také přispět svým vlastním PR, pokud víte, jak na to.
