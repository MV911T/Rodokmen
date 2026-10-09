# Rodokmen Matěje Veselého

Interaktivní rodokmen Matěje Veselého na časové ose – větve Veselý, Plachý, Woroň, Chmielek, Pacík, Matůšů, Struž a Jiřík (podle osmi praprarodičů).

**Web:** https://mv911t.github.io/Rodokmen/

## Co web umí

- **Rodokmen:** každá osoba je umístěna podle roku narození; vpravo je stupnice let a úplně vpravo sloupec historických událostí (války jako pásy, ostatní události tečkou).
- **Detail osoby** po kliknutí: data, místa, povolání, sňatky, rodiče, děti, poznámky, prameny a skeny matričních zápisů (zvětšitelné).
- **Míra doložení:** matrika / jiný doklad / rodinná tradice / kandidát.
- **Mateřská linie** (matka matky …) červeně, **otcovská linie** (otec otce …) modře.
- **Zoom:** lišta dole (−, posuvník, +, „Celý strom“, 100 %), Ctrl/⌘ + kolečko, sevření prstů na touchpadu i mobilu.
- **Odkud jsme:** mapa původu větví s doloženými přesuny, historické souvislosti a časová osa.

## Úpravy dat

Data jsou v `data.js`, ale **neupravují se ručně ani hledáním a nahrazováním** – jen přes `datatool.js`:

```js
const T = require('./datatool');
const d = T.load();
const p = T.person(d, 'karlS');    // chyba, pokud id neexistuje
p.d = { date: '…', year: 1915 };   // úprava objektu
T.save(d);                         // zapíše data.js a ověří, že se nic neztratilo
```

Po každém nálezu zrevidovat celou kartu osoby i jejích rodičů, partnera a dětí (odhady, úmrtí, pořadí poznámek – fakta první, kandidáti na konec).

## Publikace

`./publish.sh "popis změny"` – spustí `build.sh` (nejdřív kontrola konzistence `validate.js --strict`; chyba i varování publikaci zastaví), vytvoří `index.html` a odešle na GitHub Pages.

Samotná kontrola: `node validate.js`.

**Automaticky odvozené (nepsat ručně):** datum aktualizace (razítko sestavení v `build.sh`), nejstarší doložený předek (hlavička, příběhy větví, časová osa), počty osob, body na mapě z `gazetteer.js` s rokem prvního doložení. Validátor hlídá: neznámé větve a barvy, natvrdo psaná fakta v příbězích a popiscích míst, mezery v historických událostech (≥ 1 událost na 50 let) a obce chybějící v `gazetteer.js` (INFO). `publish.sh` po odeslání ověří, že web na GitHub Pages je aktuální.

Prameny: matriky Moravského zemského archivu v Brně (Acta Publica), Zemského archivu v Opavě (Digitální badatelna), SOA Třeboň, polských archivů (szukajwarchiwach.gov.pl, Skanoteka, CAAK), sčítání lidu 1930 (Slovakiana), rodinné doklady a paměti.
