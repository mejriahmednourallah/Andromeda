# 🌌 Guide d'utilisation - Andromeda

## 🚀 Démarrage du projet

### 1. Démarrer le serveur
```bash
python manage.py runserver
```

### 2. Accéder à l'application
- **URL principale** : http://127.0.0.1:8000/
- **Page de login** : http://127.0.0.1:8000/accounts/login/
- **Page d'inscription** : http://127.0.0.1:8000/accounts/signup/
- **Dashboard** : http://127.0.0.1:8000/dashboard/
- **Admin** : http://127.0.0.1:8000/admin/

---

## 🔐 Comptes utilisateurs disponibles

### Utilisateur Demo
- **Username** : `demo`
- **Password** : `demo`

### Utilisateur Admin
- **Username** : `admin`
- **Password** : `admin123`

### Autres utilisateurs
- **nour** : mot de passe à définir
- **noura** : mot de passe à définir

---

## 📱 Navigation dans l'application

### Navbar (disponible après connexion)
La barre de navigation en haut de chaque page contient :
- **Andromeda** (logo) - Retour au dashboard
- **Dashboard** - Page d'accueil avec statistiques
- **Notes** - Liste de toutes les notes
- **Souvenirs** - Liste de tous vos souvenirs
- **Avatar + Username** - Affichage du profil
- **Logout** - Déconnexion

### Pages principales

#### 1. Dashboard (`/dashboard/`)
- Statistiques : nombre de notes et souvenirs
- Actions rapides : Ajouter un souvenir, Créer une note
- Souvenirs récents (6 derniers)
- Notes récentes (5 dernières)
- Informations du compte

#### 2. Notes (`/`)
- Liste de toutes les notes
- Affichage en grille
- Accès aux détails de chaque note

#### 3. Souvenirs (`/souvenirs/`)
- Liste de tous vos souvenirs
- Affichage en cartes avec images
- Boutons : Voir détails, Supprimer
- Bouton "Nouveau souvenir" en haut

#### 4. Ajouter un souvenir (`/souvenirs/ajouter/`)
Formulaire avec :
- **Titre*** (obligatoire, min 3 caractères)
- **Description*** (obligatoire, min 10 caractères)
- **Date de l'événement*** (obligatoire, ne peut pas être dans le futur)
- **Photo** (optionnelle, formats : JPG, PNG, GIF, WebP, max 10 MB)
- **Vidéo** (optionnelle, formats : MP4, AVI, MOV, WMV, max 100 MB)

#### 5. Détail du souvenir (`/souvenirs/<id>/`)
- Titre et date de l'événement
- Photo ou vidéo si présente
- Description complète
- Métadonnées (date de création, modification)
- Actions : Supprimer, Retour

#### 6. Supprimer un souvenir (`/souvenirs/<id>/supprimer/`)
- Page de confirmation
- Affichage du souvenir à supprimer
- Warning : action irréversible
- Boutons : Confirmer ou Annuler

---

## 🎨 Design et style

### Palette de couleurs
```css
--page-bg: #f5ebe0        /* Fond beige clair */
--panel-bg: #faf6f1       /* Fond des panneaux */
--border-color: #2b2b2b   /* Bordures noires */
--accent-orange: #ff6b35  /* Orange accent */
--text-dark: #2b2b2b      /* Texte foncé */
--text-gray: #6b7280      /* Texte gris */
```

### Typographie
- **Police** : 'Courier New', monospace
- Style : Rétro, minimaliste, bordures épaisses
- Boutons : Sans arrondi, style brutalist

### Structure des pages
- Toutes les pages souvenirs utilisent `dashboard_base.html`
- Navbar sticky en haut
- Conteneur centré avec max-width
- Cards avec bordures épaisses (3px)
- Messages de feedback colorés

---

## ⚙️ Fonctionnalités

### Validation des données

#### Côté serveur (Django)
- **Titre** : 3-200 caractères
- **Description** : 10+ caractères
- **Date** : Pas dans le futur
- **Photo** : Extensions valides, max 10 MB
- **Vidéo** : Extensions valides, max 100 MB

#### Côté client (HTML)
- **Validation HTML5 désactivée** (pas de `required`)
- Validation uniquement côté serveur
- Messages d'erreur clairs en cas de problème

### Sécurité
- **Authentification requise** : Toutes les vues souvenirs
- **Vérification du propriétaire** : Seul le créateur peut voir/modifier
- **Protection CSRF** : Tous les formulaires
- **Validation des fichiers** : Type et taille
- **Logging** : Actions importantes enregistrées

### Stockage des fichiers
```
media/
├── souvenirs/
│   ├── photos/
│   │   └── 2025/
│   │       ├── 01/
│   │       ├── 02/
│   │       └── ...
│   └── videos/
│       └── 2025/
│           ├── 01/
│           ├── 02/
│           └── ...
```

---

## 🛠️ Administration

### Panel d'administration Django
URL : http://127.0.0.1:8000/admin/

**Modèles disponibles** :
- Users (utilisateurs)
- Notes
- Souvenirs
- Links
- Templates
- Attachments
- API Integrations
- AI Tasks

### Gestion des souvenirs dans l'admin
- Liste avec filtres (date, utilisateur)
- Recherche (titre, description, utilisateur)
- Hiérarchie par date
- Fieldsets organisés
- Métadonnées en lecture seule

---

## 🔧 Commandes utiles

### Créer un superuser
```bash
python manage.py createsuperuser
```

### Créer les migrations
```bash
python manage.py makemigrations
```

### Appliquer les migrations
```bash
python manage.py migrate
```

### Collecter les fichiers statiques
```bash
python manage.py collectstatic --noinput
```

### Réinitialiser un mot de passe
```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='USERNAME'); user.set_password('NOUVEAU_MDP'); user.save(); print('Mot de passe mis à jour')"
```

### Lister les utilisateurs
```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); [print(f'Username: {u.username}, Email: {u.email}') for u in User.objects.all()]"
```

---

## 📝 Notes importantes

### Validation des formulaires
- La validation HTML5 a été **désactivée** (pas de `required`)
- La validation se fait uniquement **côté serveur**
- Les erreurs s'affichent clairement en rouge

### Redirection après login
- Après connexion → **Dashboard** (`/dashboard/`)
- Après déconnexion → **Login** (`/accounts/login/`)
- Après inscription → **Dashboard**

### Responsive
- Design adaptatif pour mobile
- Menu hamburger sur petits écrans
- Grilles flexibles pour les cartes

### Performance
- Images et vidéos stockées localement
- Fichiers organisés par année/mois
- Limitation de taille pour éviter les problèmes

---

## 🐛 Dépannage

### Le login ne fonctionne pas
1. Vérifiez que vous utilisez le bon **username** (pas l'email)
2. Vérifiez le mot de passe
3. Si erreur, le message s'affiche en rouge
4. Réinitialisez le mot de passe si nécessaire

### Les fichiers média ne s'affichent pas
1. Vérifiez que `MEDIA_URL` et `MEDIA_ROOT` sont configurés
2. En développement, les URLs média sont servies automatiquement
3. Le dossier `media/` doit exister

### Erreur de migration
```bash
# Supprimer la base de données
del db.sqlite3  # Windows
rm db.sqlite3   # Linux/Mac

# Recréer les migrations
python manage.py migrate
python manage.py createsuperuser
```

### Port déjà utilisé
```bash
# Utiliser un autre port
python manage.py runserver 8001
```

---

## 📚 Documentation complète

Pour plus de détails techniques, consultez :
- `SOUVENIRS_API.md` - API et documentation technique des souvenirs
- `README.md` - Documentation générale du projet
- `BUILD_SPEC.md` - Spécifications et roadmap

---

## ✨ Prochaines fonctionnalités

- [ ] Édition de souvenirs existants
- [ ] Recherche dans les souvenirs
- [ ] Filtres par date
- [ ] Tags pour catégoriser
- [ ] Export en PDF
- [ ] Galerie de photos
- [ ] Partage de souvenirs
- [ ] Compression automatique des images
- [ ] Génération de miniatures
- [ ] Géolocalisation

---

**Version** : 1.0.0  
**Dernière mise à jour** : 24 octobre 2025
