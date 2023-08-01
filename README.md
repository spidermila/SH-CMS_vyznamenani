# SH-CMS_vyznamenani
Skript pro vytvoření přehledu vyznamenání členů SDH SH ČMS.

## Získání programu
Z této Github stránky si stáhněte aktuální verzi programu:

Verze pro Linux: ![SH-CMS_vyznamenani](https://github.com/spidermila/SH-CMS_vyznamenani/raw/main/SH-CMS_vyznamenani)

Verze pro Windows: ![SH-CMS_vyznamenani.exe](https://github.com/spidermila/SH-CMS_vyznamenani/raw/main/SH-CMS_vyznamenani.exe)

## Vstupní informace
Vstupem pro skript je textový soubor s exportem členů vašeho SDH, který může oprávněná osoba získat na webu evidencesdh.cz - viz obrázek níže:
![ukázka evidencesdh.cz](https://github.com/spidermila/SH-CMS_vyznamenani/blob/main/evidencesdh.png)

## Použití programu

Program je třeba spustit v příkazové řádce. Jako parametr použijte název textového souboru, kteý jste stáhli z evidencesdh.cz, jak je popsáno výše. S použitím parametru "-o" můžete specifikovat název výstupního souboru, jinak se výstup bude jmenovat test.xlsx.
```bash
SH-CMS_vyznamenani.exe muj_export.txt -o muj_vystup.xlsx
```

Výsledkem je tabulka MS Excel, která slouží jako přehled již získaných vyznamenání a také ukazuje podmínky pro získání vyznamenání, které ještě nebyly obdrženy.
![ukázka výsledku](https://github.com/spidermila/SH-CMS_vyznamenani/blob/main/tabulka.png)
