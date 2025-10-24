# Andromeda - Second Brain

Andromeda est une application de gestion de connaissances personnelles (second brain) qui permet de capturer, organiser et relier vos idées sous forme de notes interconnectées.

## 🌟 Fonctionnalités

### Actuellement implémenté
- ✅ Authentification utilisateur (inscription/connexion)
- ✅ Modèle de données complet (Notes, Templates, Links, Attachments)
- ✅ Interface utilisateur immersive avec design unique
- ✅ Affichage des notes
- ✅ Admin Django configuré

### En développement
- 🚧 CRUD complet pour les notes
- 🚧 Éditeur de notes riche
- 🚧 Visualisation graphe des liens
- 🚧 Recherche et filtres
- 🚧 Fonctionnalités IA (embeddings, summarization, transcription)

## 🚀 Installation

### Prérequis
- Python 3.10+
- pip

### Étapes

1. **Cloner le projet**
```bash
git clone <repository-url>
cd Andromeda-main
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Appliquer les migrations**
```bash
python manage.py migrate
```

5. **Créer un superuser**
```bash
python manage.py createsuperuser
```

6. **Lancer le serveur**
```bash
python manage.py runserver
```

7. **Accéder à l'application**
- Application : http://127.0.0.1:8000/
- Admin : http://127.0.0.1:8000/admin/

## 📁 Structure du projet

```
Andromeda-main/
├── andromeda/          # Configuration Django
│   ├── settings.py     # Paramètres
│   ├── urls.py         # URLs principales
│   └── wsgi.py         # WSGI
├── core/               # Application principale
│   ├── models.py       # Modèles (User, Note, Link, etc.)
│   ├── views.py        # Vues
│   ├── forms.py        # Formulaires
│   ├── urls.py         # URLs de l'app
│   ├── admin.py        # Configuration admin
│   └── templates/      # Templates HTML
├── static/             # Fichiers statiques
│   ├── assets/         # Images, SVG, logos
│   ├── css/            # Styles
│   ├── js/             # Scripts
│   └── images/         # Images
├── requirements.txt    # Dépendances Python
└── manage.py           # CLI Django
```

## 🎨 Design

Andromeda utilise un design unique "warm paper" avec :
- Palette de couleurs : #efe0d0 (fond), #f28a2e (accent)
- Typographie : Monospace (Courier New, ui-monospace)
- Animations CSS avancées (halo, floating, glow)
- Interface responsive

## 🔧 Technologies

- **Backend** : Django 5.2+
- **Frontend** : HTML, CSS (Tailwind CDN), JavaScript vanilla
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **API** : Django REST Framework
- **Déploiement** : Render, Gunicorn, WhiteNoise

## 📝 Modèles de données

- **User** : Utilisateur personnalisé avec avatar
- **Note** : Notes avec UUID, métadonnées JSON, support embeddings
- **Template** : Templates réutilisables (style Notion)
- **Link** : Liens entre notes (reference, derived, quote)
- **Attachment** : Fichiers attachés aux notes
- **APIIntegration** : Intégrations externes
- **AITask** : Tâches IA (embedding, transcription, summarization, OCR)

## 🧪 Tests

Exécuter les tests :
```bash
python smoke_test.py
```

## 📚 Documentation

- `BUILD_SPEC.md` : Spécifications détaillées du projet
- `GOOGLE_OAUTH_SETUP.md` : Guide pour configurer l'authentification Google

## 🔐 Sécurité

Pour la production :
- Définir `SECRET_KEY` dans les variables d'environnement
- Mettre `DEBUG=False`
- Configurer `ALLOWED_HOSTS`
- Utiliser HTTPS

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📄 Licence

[À définir]

## 👤 Auteur

[Votre nom]

## 🗺️ Roadmap

### Phase 1 (MVP)
- [x] Auth et modèles de base
- [x] UI immersive
- [ ] CRUD complet pour notes
- [ ] Recherche basique

### Phase 2
- [ ] Éditeur de notes riche
- [ ] Gestion des liens
- [ ] Upload d'attachments
- [ ] Visualisation graphe basique

### Phase 3
- [ ] Embeddings & recherche sémantique
- [ ] Workers Celery
- [ ] Fonctionnalités IA avancées
- [ ] API REST complète

### Phase 4
- [ ] Fonctionnalités équipe
- [ ] Synchronisation offline
- [ ] Intégrations externes
- [ ] Mobile app
