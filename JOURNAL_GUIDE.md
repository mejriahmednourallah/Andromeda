# Guide du Système de Journal - Andromeda

## 📝 Vue d'ensemble

Le système de journal d'Andromeda permet aux utilisateurs de créer des entrées de journal enrichies avec des tags et des humeurs pour mieux organiser et comprendre leurs pensées et émotions.

## 🗂️ Entités Principales

### 1. **EntreeJournal** (Entrée de Journal)
Représente une entrée de journal avec :
- **Champs principaux** :
  - `titre` : Titre de l'entrée (200 caractères max)
  - `contenu_texte` : Contenu de l'entrée (texte libre)
  - `utilisateur` : Propriétaire de l'entrée
  
- **Métadonnées** :
  - `lieu` : Lieu où l'entrée a été écrite
  - `meteo` : Météo du jour
  - `is_favorite` : Marquer comme favori
  - `is_public` : Rendre l'entrée publique
  
- **Propriétés calculées** :
  - `nombre_mots` : Compte automatiquement les mots
  - `tags_list` : Liste des tags associés
  - `humeurs_list` : Liste des humeurs associées

### 2. **Tag**
Permet de catégoriser les entrées :
- `nom` : Nom du tag (unique par utilisateur)
- `couleur` : Couleur en hexadécimal (#3498db)
- `description` : Description optionnelle
- `utilisateur` : Propriétaire (null = tag global)

### 3. **Humeur**
Représente une humeur/émotion :
- `nom` : Nom de l'humeur
- `emoji` : Emoji représentatif (😊)
- `couleur` : Couleur associée
- `description` : Description

**15 humeurs par défaut** : Joyeux, Triste, En colère, Anxieux, Excité, Calme, Fatigué, Motivé, Confus, Reconnaissant, Amoureux, Nostalgique, Stressé, Paisible, Créatif

### 4. **EntreeTag** (Relation)
Lie une entrée à un tag :
- `entree_journal` : L'entrée
- `tag` : Le tag
- `date_association` : Date de l'association

### 5. **EntreeHumeur** (Relation)
Lie une entrée à une humeur avec intensité :
- `entree_journal` : L'entrée
- `humeur` : L'humeur
- `intensite` : Niveau d'intensité (1-5)
- `note` : Note optionnelle sur l'humeur

## 🛣️ URLs Disponibles

### Entrées de Journal
- **Liste** : `/journal/` - Liste toutes les entrées avec filtres
- **Détail** : `/journal/<id>/` - Affiche une entrée
- **Créer** : `/journal/add/` - Créer une nouvelle entrée
- **Modifier** : `/journal/<id>/edit/` - Modifier une entrée
- **Supprimer** : `/journal/<id>/delete/` - Supprimer une entrée
- **Toggle Favori** : `/journal/<id>/favorite/` - Marquer/démarquer comme favori (AJAX)

### Tags
- **Liste** : `/journal/tags/` - Liste tous les tags
- **Créer** : `/journal/tags/add/` - Créer un tag
- **Modifier** : `/journal/tags/<id>/edit/` - Modifier un tag
- **Supprimer** : `/journal/tags/<id>/delete/` - Supprimer un tag

### Statistiques
- **Stats** : `/journal/stats/` - Statistiques du journal

## 🎨 Fonctionnalités

### Filtrage Avancé
- Par tag
- Par humeur
- Par favoris
- Recherche textuelle (titre, contenu, lieu)

### Statistiques
- Nombre total d'entrées
- Nombre total de mots écrits
- Entrées favorites
- Tags les plus utilisés (top 10)
- Humeurs les plus fréquentes (top 10)
- Entrées récentes

### Interface Admin
- Gestion complète des entrées, tags, humeurs
- Inlines pour ajouter tags/humeurs directement
- Filtres et recherche avancés
- Actions en masse (marquer comme favori)

## 💻 Utilisation du Code

### Créer une entrée de journal
```python
from core.models import EntreeJournal, Tag, Humeur, EntreeTag, EntreeHumeur

# Créer l'entrée
entree = EntreeJournal.objects.create(
    utilisateur=user,
    titre="Ma journée",
    contenu_texte="Aujourd'hui était une belle journée...",
    lieu="Paris",
    meteo="Ensoleillé"
)

# Ajouter des tags
tag = Tag.objects.get(nom="Voyage")
EntreeTag.objects.create(entree_journal=entree, tag=tag)

# Ajouter des humeurs
humeur = Humeur.objects.get(nom="Joyeux")
EntreeHumeur.objects.create(
    entree_journal=entree,
    humeur=humeur,
    intensite=4
)
```

### Filtrer les entrées
```python
# Entrées avec un tag spécifique
entrees = EntreeJournal.objects.filter(
    utilisateur=user,
    entree_tags__tag__nom="Voyage"
)

# Entrées avec une humeur
entrees = EntreeJournal.objects.filter(
    utilisateur=user,
    entree_humeurs__humeur__nom="Joyeux"
)

# Recherche textuelle
entrees = EntreeJournal.objects.filter(
    Q(titre__icontains="voyage") | Q(contenu_texte__icontains="voyage")
)
```

### Statistiques
```python
from django.db.models import Count

# Tags les plus utilisés
tags_populaires = Tag.objects.filter(
    entree_tags__entree_journal__utilisateur=user
).annotate(
    nb_utilisations=Count('entree_tags')
).order_by('-nb_utilisations')[:10]

# Humeurs fréquentes
humeurs_frequentes = Humeur.objects.filter(
    entree_humeurs__entree_journal__utilisateur=user
).annotate(
    nb_utilisations=Count('entree_humeurs')
).order_by('-nb_utilisations')[:10]
```

## 🔧 Commandes de Gestion

### Initialiser les humeurs par défaut
```bash
python manage.py init_humeurs
```

### Accéder à l'admin
```bash
# Créer un superuser si nécessaire
python manage.py createsuperuser

# Accéder à http://127.0.0.1:8000/admin/
```

## 📊 Modèle de Données

```
User (1) ──────▶ (many) EntreeJournal
                    │
                    ├──▶ (many) EntreeTag ──▶ Tag
                    │
                    └──▶ (many) EntreeHumeur ──▶ Humeur

User (1) ──────▶ (many) Tag (tags personnels)
                         + Tags globaux (utilisateur=null)
```

## 🎯 Cas d'Usage

1. **Journal quotidien** : Écrire ses pensées avec humeurs et tags
2. **Suivi émotionnel** : Analyser ses humeurs sur le temps
3. **Organisation** : Catégoriser avec des tags personnalisés
4. **Recherche** : Retrouver facilement des entrées passées
5. **Statistiques** : Comprendre ses patterns d'écriture et émotionnels

## 🔐 Sécurité

- Toutes les vues nécessitent une authentification (`@login_required`)
- Les utilisateurs ne peuvent voir/modifier que leurs propres entrées
- Les tags peuvent être personnels ou globaux
- Validation des formulaires côté serveur

## 🚀 Prochaines Étapes

Pour améliorer le système :
1. Créer les templates HTML pour l'interface utilisateur
2. Ajouter des graphiques pour les statistiques
3. Implémenter l'export PDF des entrées
4. Ajouter l'analyse IA des entrées (sentiment, suggestions de tags)
5. Créer une API REST pour une app mobile
