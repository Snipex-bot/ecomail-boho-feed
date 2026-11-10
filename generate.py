#!/usr/bin/env python3
"""Z Heureka produktového feedu vygeneruje datový feed pro Ecomail.

Výstup (feed.xml):
  <item><top>ano</top> ...3 produkty...</item>          -> kontakty s polem top = ano
  <item><kategorie>laky</kategorie> ...3 produkty...</item> -> kontakty s polem kategorie = laky

Každý produkt = p{n}nazev, p{n}cena, p{n}img, p{n}url (n = 1..PRODUCTS).

Použití:
  python3 generate.py                      # čte source/heureka.xml
  FEED_URL=https://... python3 generate.py # stáhne aktuální feed z e-shopu
"""
import json
import os
import re
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
PRODUCTS = CONFIG["products_per_block"]


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def price(value: str) -> str:
    n = round(float(value.replace(",", ".").replace(" ", "")))
    return f"{n:,}".replace(",", " ") + " Kč"


def load_items():
    url = os.environ.get("FEED_URL")
    if url:
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        (ROOT / "source" / "heureka.xml").write_bytes(data)
    else:
        data = (ROOT / "source" / "heureka.xml").read_bytes()

    items = []
    for it in ET.fromstring(data).iter("SHOPITEM"):
        cat = (it.findtext("CATEGORYTEXT") or "").split("|")[-1].strip()
        items.append({
            "id": it.findtext("ITEM_ID"),
            "nazev": (it.findtext("PRODUCTNAME") or "").replace(CONFIG.get("strip_prefix", ""), "").strip(),
            "cena": price(it.findtext("PRICE_VAT") or "0"),
            "img": (it.findtext("IMGURL") or "").strip(),
            "url": (it.findtext("URL") or "").strip(),
            "kategorie": cat,
            "skladem": (it.findtext("DELIVERY_DATE") or "").strip() == "0",
        })
    return items


def add_item(root, key, value, nadpis, products):
    item = ET.SubElement(root, "item")
    ET.SubElement(item, key).text = value
    ET.SubElement(item, "nadpis").text = nadpis
    for n, p in enumerate(products, 1):
        for field in ("nazev", "cena", "img", "url"):
            ET.SubElement(item, f"p{n}{field}").text = p[field]


def main():
    items = [i for i in load_items() if i["skladem"] and i["kategorie"] not in CONFIG["exclude_categories"]]
    by_id = {i["id"]: i for i in items}
    root = ET.Element("data")

    # 1) Bestsellery – ručně vybraná ID (feed neobsahuje data o prodejích)
    top = [by_id[i] for i in CONFIG["top_ids"] if i in by_id][:PRODUCTS]
    if len(top) == PRODUCTS:
        add_item(root, "top", "ano", CONFIG["top_title"], top)

    # 2) Kategorie – první N produktů z každé kategorie s dostatkem produktů
    cats = {}
    for i in items:
        cats.setdefault(i["kategorie"], []).append(i)
    report = []
    for name, prods in sorted(cats.items()):
        if len(prods) < PRODUCTS:
            continue
        key = slug(name)
        add_item(root, "kategorie", key, CONFIG["category_title"].format(kategorie=name), prods[:PRODUCTS])
        report.append(f"{key:30} {name} ({len(prods)} produktů)")

    ET.indent(root, space="  ")
    out = ROOT / "feed.xml"
    out.write_bytes(b'<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="utf-8"))
    print(f"top: {len(top)} produktů")
    print("Hodnoty pro pole 'kategorie':\n  " + "\n  ".join(report))


if __name__ == "__main__":
    main()
