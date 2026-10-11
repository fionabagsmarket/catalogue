# ELT Catalogue — vitrine + commande WhatsApp

Site catalogue pour un vendeur : vitrine des produits, commande via WhatsApp,
couleurs personnalisables, mélange des produits à chaque visite.
**Hébergement gratuit** sur GitHub Pages, **aucune base de données**, **aucun compte** pour les clients.

## Comment ça marche

- Les produits vivent dans `data/products.json` et la configuration dans `data/config.json`.
- La page `admin.html` (réservée au vendeur) modifie ces fichiers **directement dans le dépôt GitHub**
  via l'API officielle : chaque publication est un commit, donc historique complet et retour arrière possible.
- À chaque modification, GitHub Actions régénère automatiquement :
  - une page partageable par produit (`/produit/<slug>/`) avec son **aperçu WhatsApp dédié**
    (photo, nom et prix du produit s'affichent dans la bulle de partage) ;
  - le sitemap et les balises de partage de la page d'accueil.
- Les clients commandent sur WhatsApp : aucun compte, aucun paiement en ligne.

## Fonctionnalités

- **Bandeau compact** : le catalogue s'affiche dès le premier écran (nom, phrase d'accroche et bouton WhatsApp sur une bande fine, plus de grande page d'accueil).
- **Recherche visible et réactive** : la barre reste en haut en permanence ; dès la première lettre, défilement vers les résultats, compteur (« 8 articles trouvés pour “sac” »), mots correspondants surlignés en couleur d'accent, articles au nom correspondant en tête, état vide avec retour en un clic.
- **Mélange des produits** à chaque visite (Fisher-Yates), articles épuisés en fin de liste.
- **Chargement progressif** : le build découpe le catalogue en lots de 50 (`data/lots/`) ; la vitrine affiche le premier lot immédiatement, télécharge le reste en arrière-plan et montre les articles par vagues de 12 au défilement — conçu pour tenir plusieurs centaines d'articles sans ralentir les connexions mobiles.
- **Mises à jour visibles immédiatement** : chaque publication grave une version du catalogue dans le manifeste ; la vitrine le consulte hors cache à chaque visite et recharge les données seulement quand la version change. Les clients voient tes nouveaux articles dès leur prochaine visite, sans jamais vider leur cache.
- **Couleurs personnalisables** dans l'admin avec aperçu en direct et palettes suggérées.
- **QR code de la boutique** téléchargeable dans l'admin (à coller en boutique physique ou sur les colis).
- **« Copier le lien WhatsApp »** par produit dans l'admin : message prêt à coller dans les statuts et groupes.
- Photos compressées automatiquement en WebP avant publication ; tailles, couleurs, promos, stock et masquage par article.

## Déploiement pas à pas (~15 minutes)

### 1. Créer le dépôt GitHub
1. Créez un compte sur [github.com](https://github.com) si besoin.
2. Cliquez sur **+** (en haut à droite) → **New repository** → nommez-le (ex: `catalogue`) → **Public** → **Create**.

### 2. Envoyer les fichiers
Depuis la page du dépôt : **uploading an existing file** (lien dans la zone vide) et glissez
**tout le contenu** de ce dossier (les fichiers, pas le dossier lui-même) → **Commit changes**.

> En ligne de commande, depuis ce dossier :
> ```bash
> git init && git add -A && git commit -m "Première version du catalogue"
> git branch -M main
> git remote add origin https://github.com/VOTRE-COMPTE/catalogue.git
> git push -u origin main
> ```

### 3. Activer GitHub Pages
1. Sur le dépôt : **Settings** → **Pages** (menu de gauche).
2. Sous **Build and deployment** → **Source** : choisissez **Deploy from a branch**.
3. **Branch** : `main`, dossier `/ (root)` → **Save**.
4. Attendez ~1 minute : votre site est en ligne sur `https://VOTRE-COMPTE.github.io/catalogue/`.

### 4. Configurer l'URL du site
Ouvrez `admin.html` sur votre site (ex: `https://VOTRE-COMPTE.github.io/catalogue/admin.html`),
connectez-vous (étape 5), puis dans l'onglet **Apparence** renseignez :
- **URL publique du site** : `https://VOTRE-COMPTE.github.io/catalogue/` (indispensable pour les aperçus WhatsApp) ;
- **Numéro WhatsApp** : votre numéro au format international sans `+` ni espaces (ex: `22870901801`) ;
- le nom de la boutique, le slogan, les couleurs, la devise…
- Puis cliquez **Enregistrer l'apparence (local)** puis **💾 Publier**.

### 5. Créer le token d'administration
1. GitHub → cliquez sur votre photo → **Settings** → **Developer settings** (tout en bas).
2. **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
3. **Repository access** : *Only select repositories* → choisissez votre dépôt `catalogue`.
4. **Permissions** → **Repository permissions** → **Contents** : *Read and write*.
5. Générez, copiez le token, et collez-le dans `admin.html` pour vous connecter.

Le token reste dans votre navigateur, ne touche que ce dépôt, et peut être révoqué à tout moment.

## Gérer les produits (admin.html)

- **Ajouter / modifier** : nom, catégorie, prix, ancien prix (promo), stock, devise, description,
  photos (compressées automatiquement en WebP), tailles, couleurs, article visible ou masqué.
- **Publier** : envoie tout au GitHub. Les modifications sont d'abord locales (badge brouillon).
- **Stock à 0** : l'article reste affiché mais marqué **ÉPUISÉ**, et se place en fin de catalogue.
- **Masqué** : retiré du site et des pages produits sans être supprimé.

## Statistiques des visites (optionnel)

1. Créez un compte gratuit sur [goatcounter.com](https://www.goatcounter.com) (usage non commercial).
2. Notez le nom du site choisi (ex: `maboutique`).
3. Renseignez-le dans **admin.html → Apparence → Compte GoatCounter**, puis publiez.
4. Vos statistiques (vues par produit, clics sortants vers WhatsApp) sont sur `https://maboutique.goatcounter.com`.

## Mélange des produits

À chaque visite, la vitrine mélange aléatoirement les articles en stock (algorithme Fisher-Yates),
les articles épuisés restant en fin de liste. Le client ne tombe donc pas toujours sur les mêmes produits.

## Tester en local

```bash
python3 -m http.server 8080
```
Puis ouvrez http://localhost:8080 — l'admin affichera une erreur d'API GitHub hors ligne,
mais la vitrine fonctionne (données de `data/`).

## Structure du projet

```
├── index.html              Vitrine (couleurs et textes pilotés par config.json)
├── admin.html              Administration (produits + apparence, via API GitHub)
├── 404.html                Page d'erreur avec retour boutique
├── data/
│   ├── config.json         Identité, WhatsApp, couleurs, devise, URL du site
│   ├── products.json       Le catalogue (source unique, éditée par l'admin)
│   └── lots/               Découpage auto du catalogue (généré, ne pas éditer)
├── assets/
│   ├── hero.svg            Image du hero par défaut
│   ├── favicon.svg
│   └── produits/           Photos des articles (WebP compressé)
├── produit/                Pages produits générées (ne pas éditer à la main)
├── scripts/
│   └── build.py            Générateur (pages produits, sitemap, balises OG)
└── .github/workflows/
    └── deploy.yml          Régénère le site à chaque publication
```

## Sécurité — points clés

- Aucune donnée client n'est collectée : pas de compte, pas de formulaire, pas de cookie de suivi (hors GoatCounter si activé).
- Le token d'admin ne quitte jamais votre navigateur et ne donne accès qu'à ce dépôt ; révoquez-le depuis GitHub si besoin.
- Toute erreur de manipulation se corrige : l'historique Git conserve chaque version (onglet **Commits** → revenir à une version antérieure).
- `admin.html` est en `noindex` (non référencée) et inutilisable sans token.
- Remplacez les images SVG de démonstration par de vraies photos (JPG/WebP) : les aperçus WhatsApp sont plus efficaces avec une vraie photo.
