# 🤖 Guide d'Intégration IA avec Groq

## 🎯 Vue d'Ensemble

Ce guide explique comment configurer et utiliser l'intégration de l'IA Groq (LLaMA 3) dans votre projet Andromeda pour l'analyse avancée du journal.

---

## ⚡ Pourquoi Groq?

### Avantages de Groq
- **Ultra-rapide**: 10-100x plus rapide que les autres APIs
- **Gratuit**: API gratuite avec limites généreuses
- **Puissant**: Utilise LLaMA 3.1 70B (très performant)
- **Simple**: API compatible OpenAI
- **Fiable**: Infrastructure robuste

### Comparaison

| Fournisseur | Vitesse | Coût | Qualité |
|-------------|---------|------|---------|
| **Groq** | ⚡⚡⚡⚡⚡ | Gratuit | ⭐⭐⭐⭐⭐ |
| OpenAI GPT-4 | ⚡⚡ | $$$$ | ⭐⭐⭐⭐⭐ |
| OpenAI GPT-3.5 | ⚡⚡⚡ | $$ | ⭐⭐⭐⭐ |
| Claude | ⚡⚡⚡ | $$$ | ⭐⭐⭐⭐⭐ |

---

## 📦 Installation

### 1. Installer la bibliothèque Groq

```bash
pip install groq
```

Ou avec le fichier requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Obtenir une clé API Groq

1. **Créer un compte** sur [https://console.groq.com](https://console.groq.com)
2. **Générer une clé API**:
   - Aller dans "API Keys"
   - Cliquer sur "Create API Key"
   - Copier la clé (format: `gsk_...`)

### 3. Configurer la clé API

Ajoutez la clé dans votre fichier `.env`:

```env
GROQ_API_KEY=gsk_votre_cle_api_ici
```

**⚠️ IMPORTANT**: Ne commitez JAMAIS votre clé API sur Git!

Vérifiez que `.env` est dans `.gitignore`:

```gitignore
.env
*.env
```

---

## 🚀 Fonctionnalités IA Disponibles

### 1. 😊 **Analyse Émotionnelle**

Détecte automatiquement:
- Émotions principales (joie, tristesse, colère, etc.)
- Score de sentiment (0-1, négatif à positif)
- Intensité émotionnelle (faible/moyenne/forte)
- Thèmes émotionnels
- Résumé émotionnel

**Exemple d'utilisation:**

```python
from core.services.ai_service import get_ai_service

ai = get_ai_service()
analyse = ai.analyser_emotions("Aujourd'hui était une journée incroyable!")

# Résultat:
# {
#     "emotions_principales": ["Joie", "Enthousiasme"],
#     "sentiment_score": 0.9,
#     "themes": ["Positivité", "Gratitude"],
#     "intensite_emotionnelle": "forte",
#     "resume_emotionnel": "Journée très positive et joyeuse"
# }
```

### 2. 🏷️ **Suggestions de Tags Intelligentes**

Propose automatiquement 3-5 tags pertinents basés sur le contenu.

**Exemple:**

```python
tags = ai.suggerer_tags(
    "J'ai passé une super journée à la plage avec mes amis",
    tags_existants=["Amis", "Voyage", "Nature"]
)

# Résultat: ["Plage", "Amis", "Loisirs", "Été", "Bonheur"]
```

### 3. 📝 **Résumé Automatique**

Génère un résumé court ou moyen de l'entrée.

**Exemple:**

```python
resume = ai.generer_resume(
    "Texte long de 500 mots...",
    longueur="court"  # ou "moyen"
)

# Résultat: "Journée productive avec réunion importante et avancées sur le projet."
```

### 4. 💡 **Insights & Conseils**

Fournit:
- Observations principales
- Patterns détectés
- Suggestions constructives
- Questions de réflexion

**Exemple:**

```python
insights = ai.generer_insights("Contenu de l'entrée...")

# Résultat:
# {
#     "observation_principale": "Vous semblez très motivé par vos projets",
#     "patterns_detectes": ["Productivité", "Ambition"],
#     "suggestions": ["Prenez du temps pour vous reposer"],
#     "questions_reflexion": ["Qu'est-ce qui vous motive le plus?"]
# }
```

### 5. 📈 **Analyse de Tendances**

Analyse l'évolution émotionnelle sur plusieurs entrées (jusqu'à 10).

**Exemple:**

```python
tendances = ai.analyser_tendances([
    "Entrée 1...",
    "Entrée 2...",
    "Entrée 3..."
])

# Résultat:
# {
#     "tendance_emotionnelle": "Amélioration progressive du moral",
#     "themes_recurrents": ["Travail", "Famille", "Sport"],
#     "evolution": "positive",
#     "recommandations": ["Continuez vos activités sportives"]
# }
```

### 6. ✍️ **Prompts d'Écriture**

Génère des questions inspirantes pour encourager l'écriture.

**Exemple:**

```python
prompt = ai.generer_prompt_ecriture(contexte="humeur joyeuse")

# Résultat: "Qu'est-ce qui vous a fait sourire aujourd'hui et pourquoi?"
```

---

## 🎨 Interface Utilisateur

### Page d'Analyse IA

Accès: **`/journal/ai/`**

**Fonctionnalités:**
- ✅ Analyse émotionnelle interactive
- ✅ Suggestions de tags avec application en 1 clic
- ✅ Génération d'insights personnalisés
- ✅ Analyse de tendances sur 10 entrées
- ✅ Génération de prompts d'écriture
- ✅ Design moderne avec glassmorphism
- ✅ Animations fluides
- ✅ Résultats en temps réel

### Intégration dans le Journal

Ajoutez un bouton dans votre menu:

```html
<a href="{% url 'core:page_analyse_ai' %}" class="btn-primary">
    🤖 Analyse IA
</a>
```

---

## 🔧 Configuration Avancée

### Personnaliser le Modèle

Dans `core/services/ai_service.py`:

```python
class GroqAIService:
    def __init__(self):
        # Modèles disponibles:
        # - llama-3.1-70b-versatile (recommandé)
        # - llama-3.1-8b-instant (plus rapide)
        # - mixtral-8x7b-32768 (bon équilibre)
        self.model = "llama-3.1-70b-versatile"
```

### Ajuster la Température

```python
# Température = créativité
# 0.0 = très déterministe
# 1.0 = équilibré
# 2.0 = très créatif

response = self._call_groq(
    messages,
    temperature=0.7,  # Ajustez ici
    max_tokens=1000
)
```

### Limites de Tokens

```python
# Pour éviter les coûts:
max_tokens=500  # Réponses courtes
max_tokens=1000  # Réponses moyennes
max_tokens=2000  # Réponses longues
```

---

## 📊 Limites de l'API Groq

### Gratuit (Free Tier)

- **Requêtes/minute**: 30
- **Requêtes/jour**: 14,400
- **Tokens/minute**: 6,000
- **Tokens/requête**: 6,000

### Conseils pour Optimiser

1. **Limiter la longueur du texte**:
   ```python
   texte[:2000]  # Prendre seulement les 2000 premiers caractères
   ```

2. **Cacher les résultats**:
   ```python
   # Sauvegarder l'analyse dans la base de données
   entree.analyse_ia = json.dumps(analyse)
   entree.save()
   ```

3. **Batch processing**:
   ```python
   # Analyser plusieurs entrées en une seule requête
   ```

---

## 🛠️ Dépannage

### Erreur: "GROQ_API_KEY non trouvée"

**Solution:**
1. Vérifiez que `.env` existe
2. Vérifiez que `GROQ_API_KEY=...` est présent
3. Redémarrez le serveur Django

### Erreur: "Rate limit exceeded"

**Solution:**
- Attendez 1 minute
- Réduisez le nombre de requêtes
- Implémentez un cache

### Erreur: "Invalid API key"

**Solution:**
- Vérifiez que la clé commence par `gsk_`
- Générez une nouvelle clé sur console.groq.com
- Vérifiez qu'il n'y a pas d'espaces dans la clé

### Réponses lentes

**Solution:**
- Utilisez `llama-3.1-8b-instant` (plus rapide)
- Réduisez `max_tokens`
- Limitez la longueur du texte d'entrée

---

## 🔒 Sécurité

### Bonnes Pratiques

1. **Ne jamais exposer la clé API**:
   ```python
   # ❌ MAUVAIS
   api_key = "gsk_abc123..."
   
   # ✅ BON
   api_key = os.getenv('GROQ_API_KEY')
   ```

2. **Valider les entrées utilisateur**:
   ```python
   if len(texte) > 5000:
       texte = texte[:5000]
   ```

3. **Gérer les erreurs**:
   ```python
   try:
       analyse = ai.analyser_emotions(texte)
   except Exception as e:
       logger.error(f"Erreur IA: {e}")
       return valeur_par_defaut
   ```

4. **Rate limiting côté serveur**:
   ```python
   from django.core.cache import cache
   
   # Limiter à 10 requêtes/minute par utilisateur
   key = f"ai_requests_{user.id}"
   count = cache.get(key, 0)
   if count >= 10:
       return error_response("Trop de requêtes")
   cache.set(key, count + 1, 60)
   ```

---

## 📈 Améliorations Futures

### Idées d'Extensions

1. **Analyse de Photos**:
   - Détecter objets et scènes
   - Générer des descriptions
   - Suggérer des tags visuels

2. **Chatbot Journal**:
   - Conversation avec l'IA
   - Questions/réponses sur le journal
   - Coaching personnalisé

3. **Résumés Hebdomadaires**:
   - Synthèse automatique de la semaine
   - Highlights émotionnels
   - Recommandations

4. **Détection de Patterns**:
   - Identifier cycles émotionnels
   - Corrélations (météo, activités, humeur)
   - Prédictions

5. **Export Enrichi**:
   - PDF avec analyses IA
   - Graphiques d'évolution
   - Insights visuels

---

## 📚 Ressources

### Documentation

- **Groq API**: [https://console.groq.com/docs](https://console.groq.com/docs)
- **LLaMA 3**: [https://ai.meta.com/llama/](https://ai.meta.com/llama/)
- **Python Groq SDK**: [https://github.com/groq/groq-python](https://github.com/groq/groq-python)

### Exemples de Code

Voir les fichiers:
- `core/services/ai_service.py` - Service IA
- `core/views_ai.py` - Vues Django
- `core/templates/core/journal/analyse_ai.html` - Interface

### Support

- **Issues GitHub**: Créez une issue
- **Documentation Groq**: [https://console.groq.com/docs](https://console.groq.com/docs)
- **Discord Groq**: Rejoignez la communauté

---

## ✅ Checklist d'Installation

- [ ] Installer `groq` (`pip install groq`)
- [ ] Créer un compte sur console.groq.com
- [ ] Générer une clé API
- [ ] Ajouter `GROQ_API_KEY` dans `.env`
- [ ] Vérifier que `.env` est dans `.gitignore`
- [ ] Redémarrer le serveur Django
- [ ] Tester sur `/journal/ai/`
- [ ] Vérifier que les analyses fonctionnent
- [ ] Configurer le rate limiting (optionnel)
- [ ] Implémenter le cache (optionnel)

---

## 🎉 Conclusion

L'intégration de Groq AI apporte des fonctionnalités d'analyse avancées à votre journal:

✅ **Analyse émotionnelle automatique**
✅ **Suggestions intelligentes de tags**
✅ **Insights personnalisés**
✅ **Tendances émotionnelles**
✅ **Prompts d'écriture**
✅ **Ultra-rapide et gratuit**

**Profitez de l'IA pour enrichir votre expérience de journaling!** 🚀

---

**Dernière mise à jour:** Octobre 2025  
**Version:** 1.0  
**Statut:** ✅ Production Ready
