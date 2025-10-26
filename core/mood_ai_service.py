"""
Service d'analyse de mood utilisant OpenAI GPT
"""
import os
import json
from django.conf import settings

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class MoodAIService:
    """Service d'analyse de mood avec OpenAI"""
    
    @staticmethod
    def analyze_mood_with_openai(text: str) -> dict:
        """
        Analyse le mood avec OpenAI GPT
        
        Args:
            text: Texte à analyser
            
        Returns:
            dict avec 'top' (mood principal), 'scores' (dict), 'recommendation' (str)
        """
        if not OPENAI_AVAILABLE or not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI not configured")
        
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = f"""Analyse le mood/humeur du texte suivant et retourne un JSON avec:
1. "mood": le mood principal parmi: positif, neutre, negatif, colere, tristesse
2. "scores": un objet avec les scores pour chaque mood (positif, neutre, negatif, colere, tristesse) entre 0 et 1
3. "recommendation": une recommandation personnalisée en français (2-3 phrases) basée sur le mood détecté

Texte à analyser:
"{text}"

Réponds UNIQUEMENT avec un JSON valide, sans texte supplémentaire."""

        try:
            response = client.chat.completions.create(
                model=settings.AI_TEXT_MODEL,
                messages=[
                    {"role": "system", "content": "Tu es un expert en analyse émotionnelle et psychologie positive. Tu fournis des analyses précises et des recommandations bienveillantes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON si nécessaire
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            # Valider et normaliser les scores
            scores = result.get('scores', {})
            normalized_scores = {
                'positif': float(scores.get('positif', 0)),
                'neutre': float(scores.get('neutre', 0)),
                'negatif': float(scores.get('negatif', 0)),
                'colere': float(scores.get('colere', 0)),
                'tristesse': float(scores.get('tristesse', 0))
            }
            
            return {
                'top': result.get('mood', 'neutre'),
                'scores': normalized_scores,
                'recommendation': result.get('recommendation', 'Continuez à prendre soin de vous.')
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Erreur de parsing JSON: {e}")
        except Exception as e:
            raise ValueError(f"Erreur OpenAI: {e}")
    
    @staticmethod
    def get_fallback_analysis(text: str) -> dict:
        """
        Analyse de secours basique si OpenAI n'est pas disponible
        """
        t = (text or '').lower()
        pos = ['super', 'bien', 'génial', 'genial', 'heureux', 'joie', 'content', 'love', 'aime', 'fier']
        neg = ['mauvais', 'nul', 'triste', 'déprimé', 'deprime', 'peur', 'anxieux', 'stress', 'mal']
        anger = ['colère', 'colere', 'furieux', 'énervé', 'enerve', 'rage', 'agacé', 'agace']
        sad = ['triste', 'tristesse', 'chagrin', 'pleurer', 'solitaire']
        
        scores = {'positif': 0.0, 'neutre': 0.1, 'negatif': 0.0, 'colere': 0.0, 'tristesse': 0.0}
        
        for w in pos:
            if w in t: scores['positif'] += 1
        for w in neg:
            if w in t: scores['negatif'] += 1
        for w in anger:
            if w in t: scores['colere'] += 1
        for w in sad:
            if w in t: scores['tristesse'] += 1
        
        if scores['positif']==0 and scores['negatif']==0 and scores['colere']==0 and scores['tristesse']==0:
            scores['neutre'] = 1.0
        
        top = max(scores, key=scores.get)
        
        recommendations = {
            'positif': "Garde cette énergie: note 3 gratitudes et planifie une petite action qui te fait plaisir.",
            'neutre': "Prends 2 minutes pour respirer et écrire une intention simple pour aujourd'hui.",
            'negatif': "Fais une pause courte (5 min), respire 4-7-8 et écris ce qui te pèse pour l'externaliser.",
            'colere': "Évite d'agir à chaud. 10 respirations profondes ou une marche brève pour apaiser la tension.",
            'tristesse': "Autorise-toi à ressentir. Appelle une personne de confiance ou écoute une musique douce."
        }
        
        return {
            'top': top,
            'scores': scores,
            'recommendation': recommendations.get(top, recommendations['neutre'])
        }
