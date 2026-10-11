#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur du site statique.
Lit data/config.json et data/products.json et produit :
  - produit/<slug>/index.html  (page partageable, aperçu WhatsApp par produit)
  - sitemap.xml, robots.txt
  - met à jour les balises OG de index.html
Lancé par GitHub Actions à chaque modification des données,
ou en local : python3 scripts/build.py
"""
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote

RACINE = Path(__file__).resolve().parent.parent

cfg = json.loads((RACINE / "data" / "config.json").read_text(encoding="utf-8"))
produits = json.loads((RACINE / "data" / "products.json").read_text(encoding="utf-8"))

nom_boutique = cfg.get("nom_boutique") or "Boutique"
devise_defaut = cfg.get("devise") or "FCFA"
base = (cfg.get("site_url") or "https://exemple.github.io/catalogue/").rstrip("/") + "/"
whatsapp = re.sub(r"\D", "", str(cfg.get("whatsapp") or ""))
couleurs = {"fond": "#F7F3EE", "nav": "#140F0A", "accent": "#B5893F", "texte": "#1A1410"}
couleurs.update(cfg.get("couleurs") or {})


def echapper(s):
    return (str(s if s is not None else "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def absolu(url):
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return base + url.lstrip("/")


def depuis_racine(url):
    """Chemin utilisable depuis /produit/<slug>/ : les chemins relatifs
    remontent de deux niveaux, les URLs absolues restent telles quelles."""
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return "../../" + url.lstrip("/")


def page_produit(p):
    devise = p.get("devise") or devise_defaut
    prix = p.get("prix") or 0
    prix_barre = p.get("prix_barre")
    en_rupture = not p.get("stock")
    en_promo = bool(prix_barre and prix_barre > prix)
    image_principale = absolu(p.get("images", [p.get("image") or ""])[0])
    lien_produit = absolu(f"produit/{p['slug']}/")
    message = (f"Bonjour {nom_boutique} ! 👋\nJe veux commander :\n\n"
               f"🏷️ *{p['nom']}*\n💰 {prix:,} {devise}\n🔗 {lien_produit}".replace(",", " "))
    wa = "https://wa.me/" + whatsapp + "?text=" + quote(message)

    images = p.get("images") or ([p["image"]] if p.get("image") else [])
    images_page = [depuis_racine(img) for img in images]
    vignettes = ""
    if len(images_page) > 1:
        vignettes = '<div class="vignettes">' + "".join(
            f'<img src="{echapper(img)}" alt="" loading="lazy" />' for img in images_page[1:]) + "</div>"

    badge = ""
    if en_rupture:
        badge = '<span class="badge rupture">ÉPUISÉ</span>'
    elif en_promo:
        badge = f'<span class="badge">-{round((1 - prix / prix_barre) * 100)}%</span>'
    promo_prix = f' <span class="promo">{prix_barre:,}</span>'.replace(",", " ") if en_promo else ""

    opts = ""
    if p.get("tailles"):
        opts += ('<div style="font-size:.72rem;text-transform:uppercase;color:#999;margin-top:14px">Tailles</div>'
                 '<div class="opts">' + "".join(f'<span class="opt">{echapper(t)}</span>' for t in p["tailles"]) + "</div>")
    if p.get("couleurs"):
        opts += ('<div style="font-size:.72rem;text-transform:uppercase;color:#999;margin-top:14px">Couleurs</div>'
                 '<div class="opts">' + "".join(f'<span class="opt">{echapper(c)}</span>' for c in p["couleurs"]) + "</div>")

    gc_code = re.sub(r"[^a-zA-Z0-9-]", "", str(cfg.get("goatcounter") or ""))
    gc = ""
    if gc_code:
        gc = f'<script async src="https://gc.zgo.at/count.js" data-goatcounter="https://{echapper(gc_code)}.goatcounter.com/count"></script>'

    description = echapper(p.get("description") or "").replace("\n", "<br>")
    titre_og = f"{p['nom']} — {nom_boutique}"
    desc_og = f"{prix:,} {devise}".replace(",", " ") + (" — Épuisé" if en_rupture else "")

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{echapper(titre_og)}</title>
  <meta name="description" content="{echapper(desc_og)}" />
  <meta property="og:title" content="{echapper(titre_og)}" />
  <meta property="og:description" content="{echapper(desc_og)}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{echapper(lien_produit)}" />
  <meta property="og:image" content="{echapper(image_principale)}" />
  <meta property="og:image:alt" content="{echapper(p['nom'])}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{echapper(titre_og)}" />
  <meta name="twitter:description" content="{echapper(desc_og)}" />
  <meta name="twitter:image" content="{echapper(image_principale)}" />
  <meta name="theme-color" content="{echapper(couleurs['nav'])}" />
  <style>
    :root{{--fond:{couleurs['fond']};--nav:{couleurs['nav']};--accent:{couleurs['accent']};--texte:{couleurs['texte']};--pierre:#E8DDD2;--wa:#25D366}}
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:'Plus Jakarta Sans','Segoe UI',sans-serif;background:var(--fond);color:var(--texte);line-height:1.6}}
    .barre{{background:var(--nav);height:56px;display:flex;align-items:center;justify-content:space-between;padding:0 20px}}
    .barre a{{font-family:Georgia,serif;color:var(--accent);font-size:1.25rem;letter-spacing:3px;text-transform:uppercase;text-decoration:none}}
    .barre .retour{{font-size:.8rem;color:#fff;text-decoration:none;opacity:.85;letter-spacing:0;text-transform:none}}
    main{{max-width:860px;margin:0 auto;padding:32px 20px 60px}}
    .grille{{display:grid;grid-template-columns:1fr;gap:28px}}
    @media(min-width:720px){{.grille{{grid-template-columns:1fr 1fr;align-items:start}}}}
    .photo{{width:100%;border-radius:16px;background:var(--pierre);box-shadow:0 6px 30px rgba(0,0,0,.1)}}
    .photo img{{width:100%;border-radius:16px;display:block;object-fit:cover}}
    .vignettes{{display:flex;gap:8px;margin-top:10px;overflow-x:auto}}
    .vignettes img{{width:70px;height:70px;object-fit:cover;border-radius:8px}}
    h1{{font-family:Georgia,serif;font-size:2rem;line-height:1.15;margin-bottom:10px}}
    .prix{{font-size:1.4rem;font-weight:700;color:var(--accent);margin-bottom:4px}}
    .promo{{color:#999;text-decoration:line-through;font-size:.95rem}}
    .badge{{display:inline-block;background:#C0392B;color:#fff;font-size:.72rem;font-weight:700;padding:3px 10px;border-radius:100px;margin-bottom:12px}}
    .rupture{{background:rgba(0,0,0,.6)}}
    .desc{{margin:18px 0;color:#555}}
    .opts{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 20px}}
    .opt{{border:1px solid var(--pierre);border-radius:8px;padding:6px 14px;font-size:.85rem}}
    .wa{{display:block;background:var(--wa);color:#fff;text-align:center;padding:16px;border-radius:12px;font-weight:700;text-decoration:none;font-size:1rem}}
    .wa.desactive{{background:#bbb;pointer-events:none}}
    .btn-secondaire{{display:block;text-align:center;margin-top:12px;padding:14px;border-radius:12px;border:1.5px solid var(--texte);color:var(--texte);text-decoration:none;font-weight:600;font-size:.9rem}}
    .note{{text-align:center;color:#999;font-size:.75rem;margin-top:26px}}
  </style>
</head>
<body>
  <div class="barre">
    <a href="{echapper(base)}">{echapper(nom_boutique)}</a>
    <a class="retour" href="{echapper(base)}">← Voir tout le catalogue</a>
  </div>
  <main>
    <div class="grille">
      <div class="photo">
        <img src="{echapper(images_page[0] if images_page else '')}" alt="{echapper(p['nom'])}" />
        {vignettes}
      </div>
      <div>
        {badge}
        <h1>{echapper(p['nom'])}</h1>
        <div class="prix">{prix:,} {echapper(devise)}{promo_prix}</div>
        {opts}
        <div class="desc">{description}</div>
        <a class="wa {'desactive' if en_rupture else ''}" href="{echapper(wa)}" target="_blank" rel="noopener">{'Produit indisponible' if en_rupture else 'Commander sur WhatsApp'}</a>
        <a class="btn-secondaire" href="{echapper(base)}">Voir les autres articles</a>
      </div>
    </div>
    <p class="note">Paiement et livraison organisés directement sur WhatsApp avec {echapper(nom_boutique)}.</p>
  </main>
  {gc}
</body>
</html>
"""


def maj_og_index():
    chemin = RACINE / "index.html"
    html = chemin.read_text(encoding="utf-8")
    bloc = (
        f'  <meta property="og:title" content="{echapper(nom_boutique)} — Boutique Officielle" />\n'
        f'  <meta property="og:description" content="{echapper(cfg.get("texte_hero") or cfg.get("slogan") or "Commandez en ligne.")}" />\n'
        f'  <meta property="og:type" content="website" />\n'
        f'  <meta property="og:url" content="{echapper(base)}" />\n'
        f'  <meta property="og:image" content="{echapper(absolu(cfg.get("image_partage") or "assets/hero.svg"))}" />'
    )
    html = re.sub(r"<!-- OG:AUTO[\s\S]*?<!-- OG:FIN -->",
                  "<!-- OG:AUTO -->\n" + bloc + "\n  <!-- OG:FIN -->", html)
    html = re.sub(r"<title>[\s\S]*?</title>", f"<title>{echapper(nom_boutique)} — Boutique Officielle</title>", html)
    html = re.sub(r'<meta name="theme-color" content="[^"]*"\s*/?>',
                  f'<meta name="theme-color" content="{echapper(couleurs["nav"])}" />', html)
    chemin.write_text(html, encoding="utf-8")


def sitemap():
    urls = [base] + [absolu(f"produit/{p['slug']}/") for p in produits
                     if p.get("actif") is not False and p.get("slug")]
    corps = "\n".join(f"  <url><loc>{echapper(u)}</loc></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + corps + "\n</urlset>\n")


# ---------- Exécution ----------
dir_produits = RACINE / "produit"
if dir_produits.exists():
    shutil.rmtree(dir_produits)
dir_produits.mkdir(parents=True)

total = 0
for p in produits:
    if p.get("actif") is False or not p.get("slug"):
        continue
    dossier = dir_produits / p["slug"]
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "index.html").write_text(page_produit(p), encoding="utf-8")
    total += 1

(RACINE / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
(RACINE / "robots.txt").write_text(
    "User-agent: *\nAllow: /\nDisallow: /admin.html\n\nSitemap: " + base + "sitemap.xml\n", encoding="utf-8")

# ---------- Découpage du catalogue en lots (chargement progressif) ----------
# La vitrine charge le premier lot immédiatement, le reste en arrière-plan.
# products.json reste la source unique éditée par l'admin : seul le build découpe.
taille_lot = int(os.environ.get("TAILLE_LOT", "50"))
actifs = [p for p in produits if p.get("actif") is not False]

# Empreinte du catalogue + de la config : change à chaque publication.
# La vitrine s'en sert pour invalider le cache navigateur des clients.
empreinte = hashlib.sha1()
empreinte.update((RACINE / "data" / "products.json").read_bytes())
empreinte.update((RACINE / "data" / "config.json").read_bytes())
version = empreinte.hexdigest()[:10]

dir_lots = RACINE / "data" / "lots"
if dir_lots.exists():
    shutil.rmtree(dir_lots)
dir_lots.mkdir(parents=True)
noms_lots = []
for debut in range(0, len(actifs), taille_lot):
    nom = f"lot-{len(noms_lots) + 1}.json"
    (dir_lots / nom).write_text(
        json.dumps(actifs[debut:debut + taille_lot], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    noms_lots.append(nom)
(dir_lots / "manifest.json").write_text(
    json.dumps({"total": len(actifs), "taille_lot": taille_lot, "version": version, "lots": noms_lots},
               ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8")

maj_og_index()

print(f"✓ {total} page(s) produit générée(s) dans /produit")
print(f"✓ catalogue découpé en {len(noms_lots)} lot(s) de {taille_lot} — version du build : {version}")
print("✓ sitemap.xml, robots.txt et balises OG de index.html mis à jour")
