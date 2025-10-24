# 📸 Module Souvenirs - Documentation

## Vue d'ensemble

Le module Souvenirs permet aux utilisateurs d'Andromeda d'enregistrer et de gérer leurs souvenirs personnels avec des photos et vidéos.

## Modèle de données

### Souvenir

| Champ | Type | Description | Obligatoire |
|-------|------|-------------|-------------|
| `id` | UUID | Identifiant unique | ✅ Auto-généré |
| `utilisateur` | ForeignKey | Utilisateur propriétaire | ✅ |
| `titre` | CharField(200) | Titre du souvenir | ✅ |
| `description` | TextField | Description détaillée | ✅ |
| `date_evenement` | DateField | Date de l'événement | ✅ |
| `photo` | ImageField | Photo du souvenir | ❌ |
| `video` | FileField | Vidéo du souvenir | ❌ |
| `created_at` | DateTimeField | Date de création | ✅ Auto |
| `updated_at` | DateTimeField | Date de modification | ✅ Auto |

## Validations

### Validations automatiques

1. **Titre** :
   - Minimum 3 caractères
   - Maximum 200 caractères
   - Ne peut pas être vide

2. **Description** :
   - Minimum 10 caractères
   - Ne peut pas être vide

3. **Date événement** :
   - Ne peut pas être dans le futur

4. **Photo** :
   - Formats acceptés : JPG, JPEG, PNG, GIF, WebP
   - Taille maximale : 10 MB

5. **Vidéo** :
   - Formats acceptés : MP4, AVI, MOV, WMV, MKV
   - Taille maximale : 100 MB

## URLs disponibles

| URL | Nom | Description | Auth requise |
|-----|-----|-------------|--------------|
| `/souvenirs/` | `liste_souvenirs` | Liste des souvenirs | ✅ |
| `/souvenirs/ajouter/` | `ajouter_souvenir` | Ajouter un souvenir | ✅ |
| `/souvenirs/<uuid>/` | `detail_souvenir` | Détail d'un souvenir | ✅ |
| `/souvenirs/<uuid>/supprimer/` | `supprimer_souvenir` | Supprimer un souvenir | ✅ |

## Vues

### `ajouter_souvenir(request)`

Fonction pour ajouter un nouveau souvenir.

**Méthode** : GET, POST  
**Authentification** : Requise  
**Permissions** : Utilisateur connecté

**Paramètres POST** :
- `titre` : Titre du souvenir
- `description` : Description du souvenir
- `date_evenement` : Date de l'événement (format YYYY-MM-DD)
- `photo` : Fichier image (optionnel)
- `video` : Fichier vidéo (optionnel)

**Retours** :
- Succès : Redirection vers `liste_souvenirs` avec message de succès
- Erreur : Affichage du formulaire avec messages d'erreur

**Exemple d'utilisation Python** :

```python
from django.contrib.auth import get_user_model
from core.models import Souvenir
from datetime import date

User = get_user_model()
user = User.objects.get(username='demo')

souvenir = Souvenir.objects.create(
    utilisateur=user,
    titre="Mon premier voyage",
    description="Un souvenir inoubliable de mes vacances à Paris",
    date_evenement=date(2024, 7, 15)
)
```

### `liste_souvenirs(request)`

Affiche la liste des souvenirs de l'utilisateur connecté.

**Méthode** : GET  
**Authentification** : Requise  
**Permissions** : Utilisateur connecté

**Retours** :
- Liste des souvenirs triés par date d'événement (plus récent en premier)

### `detail_souvenir(request, souvenir_id)`

Affiche le détail d'un souvenir spécifique.

**Méthode** : GET  
**Authentification** : Requise  
**Permissions** : Propriétaire du souvenir uniquement

**Paramètres** :
- `souvenir_id` : UUID du souvenir

**Retours** :
- Détail complet du souvenir
- 404 si le souvenir n'existe pas ou n'appartient pas à l'utilisateur

### `supprimer_souvenir(request, souvenir_id)`

Supprime un souvenir après confirmation.

**Méthode** : GET, POST  
**Authentification** : Requise  
**Permissions** : Propriétaire du souvenir uniquement

**Paramètres** :
- `souvenir_id` : UUID du souvenir

**Retours** :
- GET : Page de confirmation
- POST : Suppression et redirection vers `liste_souvenirs`

## Sécurité

### Mesures de sécurité implémentées

1. **Authentification obligatoire** : Toutes les vues nécessitent l'authentification via `@login_required`

2. **Validation des propriétaires** : Chaque vue vérifie que l'utilisateur est bien le propriétaire du souvenir

3. **Protection CSRF** : Tous les formulaires incluent `{% csrf_token %}`

4. **Validation des fichiers** :
   - Vérification des extensions de fichiers
   - Limitation de la taille des fichiers
   - Validation des types MIME

5. **Sanitization des données** :
   - `.strip()` appliqué sur les champs texte
   - Validation de longueur minimale/maximale

6. **Logging** : Toutes les actions importantes sont enregistrées

## Utilisation du formulaire

### Exemple HTML

```html
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Enregistrer</button>
</form>
```

### Exemple avec gestion d'erreurs

```python
from core.forms import SouvenirForm

if request.method == 'POST':
    form = SouvenirForm(request.POST, request.FILES)
    if form.is_valid():
        souvenir = form.save(commit=False)
        souvenir.utilisateur = request.user
        souvenir.save()
        # Succès
    else:
        # Afficher les erreurs
        print(form.errors)
```

## Administration Django

Le modèle `Souvenir` est enregistré dans l'admin Django avec les fonctionnalités suivantes :

- Liste des souvenirs avec filtres
- Recherche par titre, description et utilisateur
- Hiérarchie de dates
- Fieldsets organisés
- Champs en lecture seule pour les métadonnées

**Accès** : http://localhost:8000/admin/core/souvenir/

## Tests

### Tester la création d'un souvenir

```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import Souvenir
from datetime import date

class SouvenirTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_create_souvenir(self):
        response = self.client.post('/souvenirs/ajouter/', {
            'titre': 'Test Souvenir',
            'description': 'Ceci est une description de test',
            'date_evenement': '2024-01-15'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Souvenir.objects.count(), 1)
```

## Migration et déploiement

### Commandes nécessaires

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer le répertoire media (si nécessaire)
mkdir media

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

### Configuration production

Assurez-vous d'avoir dans `settings.py` :

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

Et dans `urls.py` (pour le développement) :

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Stockage des fichiers

### Structure des dossiers

```
media/
├── souvenirs/
│   ├── photos/
│   │   ├── 2024/
│   │   │   ├── 01/
│   │   │   ├── 02/
│   │   │   └── ...
│   └── videos/
│       ├── 2024/
│       │   ├── 01/
│       │   ├── 02/
│       │   └── ...
```

Les fichiers sont organisés par année et mois pour faciliter la gestion.

## Améliorations futures possibles

1. **Géolocalisation** : Ajouter des coordonnées GPS
2. **Tags** : Système de tags pour catégoriser les souvenirs
3. **Partage** : Permettre le partage de souvenirs entre utilisateurs
4. **Galerie** : Vue en galerie pour les photos
5. **Compression** : Compression automatique des images
6. **Thumbnails** : Génération de miniatures
7. **Export** : Export des souvenirs en PDF
8. **Recherche** : Recherche full-text dans les souvenirs

## Support

Pour toute question ou problème, consultez le fichier `README.md` ou créez une issue sur GitHub.
