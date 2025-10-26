"""
Service de recommandation musicale basé sur l'état émotionnel
"""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available for music recommendations")


class MusicRecommendationService:
    """Service pour recommander de la musique selon l'émotion"""
    
    @staticmethod
    def get_music_recommendation(user_text: str, detected_mood: str = None) -> dict:
        """
        Recommande une chanson basée sur le texte et l'émotion détectée
        
        Args:
            user_text: Le texte de réflexion de l'utilisateur
            detected_mood: L'émotion détectée (optionnel)
            
        Returns:
            dict avec 'emotion', 'suggestion', 'description'
        """
        if not OPENAI_AVAILABLE or not settings.OPENAI_API_KEY:
            return MusicRecommendationService._get_fallback_recommendation(detected_mood or 'neutre')
        
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            mood_context = f"\nL'analyse émotionnelle a détecté: {detected_mood}" if detected_mood else ""
            
            prompt = f"""Tu es un assistant de bien-être émotionnel intégré dans une application de réflexion personnelle. 
L'utilisateur écrit une réflexion pour exprimer son état émotionnel. 
Analyse le texte et propose une chanson qui correspond à son émotion du moment.{mood_context}

Texte de l'utilisateur :
"{user_text}"

1. Analyse le ton émotionnel général (par exemple : tristesse, motivation, stress, joie, confusion, amour, solitude...).
2. Recommande une chanson (titre + artiste) qui correspond à cette émotion.
3. Explique brièvement (2 phrases maximum) pourquoi cette chanson est adaptée.
4. Le style doit rester calme, bienveillant et inspirant, adapté à un tableau de bord de bien-être moderne.

Format de réponse JSON :
{{
  "emotion": "<émotion détectée>",
  "suggestion": "<titre - artiste>",
  "description": "<courte explication>"
}}

Réponds UNIQUEMENT avec un JSON valide, sans texte supplémentaire."""

            response = client.chat.completions.create(
                model=settings.AI_TEXT_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un expert en musicothérapie et bien-être émotionnel. Tu recommandes des chansons apaisantes et adaptées à l'état émotionnel de l'utilisateur."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
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
            
            return {
                'emotion': result.get('emotion', detected_mood or 'neutre'),
                'suggestion': result.get('suggestion', 'No suggestion available'),
                'description': result.get('description', 'Profitez de cette musique pour vous détendre.')
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in music recommendation: {e}")
            return MusicRecommendationService._get_fallback_recommendation(detected_mood or 'neutre')
        except Exception as e:
            logger.error(f"Error getting music recommendation: {e}")
            return MusicRecommendationService._get_fallback_recommendation(detected_mood or 'neutre')
    
    @staticmethod
    def _get_fallback_recommendation(mood: str) -> dict:
        """
        Recommandations de secours si l'API n'est pas disponible
        """
        fallback_recommendations = {
            'positif': {
                'emotion': 'Joie et positivité',
                'suggestion': 'Happy - Pharrell Williams',
                'description': 'Un classique énergisant qui célèbre le bonheur et la bonne humeur. Parfait pour prolonger votre état d\'esprit positif.'
            },
            'neutre': {
                'emotion': 'Calme et sérénité',
                'suggestion': 'Weightless - Marconi Union',
                'description': 'Une composition relaxante scientifiquement conçue pour réduire l\'anxiété. Idéale pour un moment de tranquillité.'
            },
            'negatif': {
                'emotion': 'Tristesse et réflexion',
                'suggestion': 'Fix You - Coldplay',
                'description': 'Une chanson réconfortante qui accompagne doucement les moments difficiles. Elle rappelle que les choses s\'amélioreront.'
            },
            'colere': {
                'emotion': 'Frustration et tension',
                'suggestion': 'Breathe Me - Sia',
                'description': 'Une mélodie apaisante pour relâcher les tensions. Aide à transformer la colère en introspection constructive.'
            },
            'tristesse': {
                'emotion': 'Mélancolie',
                'suggestion': 'The Night We Met - Lord Huron',
                'description': 'Une ballade touchante qui valide vos émotions tout en offrant du réconfort. Permet de ressentir et d\'accepter la tristesse.'
            }
        }
        
        return fallback_recommendations.get(
            mood.lower(), 
            fallback_recommendations['neutre']
        )
