# ecomail-boho-feed

Datový feed pro Ecomail (Boho Cosmetics), generovaný z Heureka produktového feedu.

**URL feedu pro Ecomail** (Další → Datové feedy):
`https://raw.githubusercontent.com/<owner>/ecomail-boho-feed/main/feed.xml`

## Jak to funguje
1. GitHub Action (`.github/workflows/update-feed.yml`) denně stáhne Heureka feed (secret `FEED_URL`).
2. `generate.py` z něj vytvoří `feed.xml`:
   - `<top>ano</top>` – ručně vybrané produkty (`config.json` → `top_ids`; Heureka feed nemá data o prodejích)
   - `<kategorie>slug</kategorie>` – první 3 skladové produkty z každé kategorie (min. 3 produkty)
3. Ecomail feed synchronizuje a dosazuje obsah podle polí kontaktu.

## Pole u kontaktů
| Pole | Hodnota | Zobrazí |
|---|---|---|
| `top` | `ano` | bestsellery |
| `kategorie` | např. `rtenky`, `laky-na-nehty`, `ocni-stiny` | 3 produkty z kategorie |

Seznam platných hodnot vypíše `python3 generate.py`.

## Merge tagy do šablony (ID feedu např. `ux473`)
```
*|ECM_DATAFEED_ux473_kategorie_nadpis|*
*|ECM_DATAFEED_ux473_kategorie_p1nazev|*
*|ECM_DATAFEED_ux473_kategorie_p1cena|*
*|ECM_DATAFEED_ux473_kategorie_p1img|*   -> Dynamický obrázek
*|ECM_DATAFEED_ux473_kategorie_p1url|*   -> odkaz obrázku / tlačítka
```
Pro bestsellery nahraďte `kategorie` za `top`. Produkty 2 a 3: `p2…`, `p3…`.

Obsah feedu se nezobrazí v náhledu editoru – testujte přes **Testování** v automatizaci.
