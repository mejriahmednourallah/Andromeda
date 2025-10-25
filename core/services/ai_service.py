"""
Service d'Intelligence Artificielle avec Groq API
Utilise LLaMA 3 pour l'analyse avancée du journal
"""

import os
from typing import Dict, List, Optional
import json
from groq import Groq


class GroqAIService:
    """Service d'IA utilisant l'API Groq pour l'analyse du journal"""
    
    def __init__(self):
        """Initialise le client Groq avec la clé API"""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY non trouvée dans les variables d'environnement")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Nouveau modèle (mis à jour)
    
    def _call_groq(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Appelle l'API Groq
        
        Args:
            messages: Liste de messages pour la conversation
            temperature: Créativité (0.0-2.0)
            max_tokens: Nombre maximum de tokens
            
        Returns:
            Réponse de l'IA
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Erreur Groq API: {e}")
            return None
    
    def analyser_emotions(self, texte: str) -> Dict:
        """
        Analyse les émotions présentes dans le texte
        
        Args:
            texte: Contenu de l'entrée de journal
            
        Returns:
            Dict avec émotions détectées, score de sentiment, thèmes
        """
        messages = [
            {
                "role": "system",
                "content": """Tu es un expert en analyse émotionnelle. Analyse le texte fourni et retourne un JSON avec:
                {
                    "emotions_principales": ["émotion1", "émotion2", "émotion3"],
                    "sentiment_score": 0.0 à 1.0 (0=très négatif, 0.5=neutre, 1=très positif),
                    "themes": ["thème1", "thème2"],
                    "intensite_emotionnelle": "faible/moyenne/forte",
                    "resume_emotionnel": "description courte"
                }
                Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire."""
            },
            {
                "role": "user",
                "content": f"Analyse ce texte de journal intime:\n\n{texte[:2000]}"  # Limite à 2000 caractères
            }
        ]
        
        response = self._call_groq(messages, temperature=0.3, max_tokens=500)
        
        if response:
            try:
                # Nettoyer la réponse pour extraire uniquement le JSON
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                return json.loads(response)
            except json.JSONDecodeError:
                print(f"Erreur de parsing JSON: {response}")
                return self._get_default_emotion_analysis()
        
        return self._get_default_emotion_analysis()
    
    def suggerer_tags(self, texte: str, tags_existants: List[str] = None) -> List[str]:
        """
        Suggère des tags pertinents pour l'entrée
        
        Args:
            texte: Contenu de l'entrée
            tags_existants: Liste des tags déjà utilisés par l'utilisateur
            
        Returns:
            Liste de 3-5 tags suggérés
        """
        tags_context = ""
        if tags_existants:
            tags_context = f"\nTags existants de l'utilisateur: {', '.join(tags_existants[:20])}"
        
        messages = [
            {
                "role": "system",
                "content": f"""Tu es un expert en catégorisation de contenu. Suggère 3 à 5 tags pertinents pour ce texte de journal.
                Les tags doivent être:
                - Courts (1-2 mots)
                - Pertinents au contenu
                - En français
                - Utiles pour retrouver l'entrée plus tard
                {tags_context}
                
                Réponds avec une liste JSON simple: ["tag1", "tag2", "tag3"]
                Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire."""
            },
            {
                "role": "user",
                "content": f"Texte:\n\n{texte[:1500]}"
            }
        ]
        
        response = self._call_groq(messages, temperature=0.5, max_tokens=200)
        
        if response:
            try:
                # Nettoyer la réponse
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                tags = json.loads(response)
                return tags[:5]  # Maximum 5 tags
            except json.JSONDecodeError:
                return []
        
        return []
    
    def generer_resume(self, texte: str, longueur: str = "court") -> str:
        """
        Génère un résumé de l'entrée
        
        Args:
            texte: Contenu de l'entrée
            longueur: "court" (1-2 phrases) ou "moyen" (3-5 phrases)
            
        Returns:
            Résumé du texte
        """
        longueur_instruction = "1 à 2 phrases" if longueur == "court" else "3 à 5 phrases"
        
        messages = [
            {
                "role": "system",
                "content": f"""Tu es un expert en résumé de texte. Résume ce texte de journal intime en {longueur_instruction}.
                Le résumé doit capturer l'essence et les points clés du texte.
                Réponds directement avec le résumé, sans introduction."""
            },
            {
                "role": "user",
                "content": f"Texte à résumer:\n\n{texte}"
            }
        ]
        
        response = self._call_groq(messages, temperature=0.3, max_tokens=300)
        return response if response else "Résumé non disponible"
    
    def generer_insights(self, texte: str) -> Dict:
        """
        Génère des insights et observations sur l'entrée
        
        Args:
            texte: Contenu de l'entrée
            
        Returns:
            Dict avec insights, patterns, suggestions
        """
        messages = [
            {
                "role": "system",
                "content": """Tu es un coach de vie et psychologue. Analyse ce texte de journal et fournis des insights.
                Retourne un JSON avec:
                {
                    "observation_principale": "observation clé",
                    "patterns_detectes": ["pattern1", "pattern2"],
                    "suggestions": ["suggestion1", "suggestion2"],
                    "questions_reflexion": ["question1", "question2"]
                }
                Sois bienveillant, constructif et respectueux.
                Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire."""
            },
            {
                "role": "user",
                "content": f"Texte:\n\n{texte[:2000]}"
            }
        ]
        
        response = self._call_groq(messages, temperature=0.6, max_tokens=800)
        
        if response:
            try:
                # Nettoyer la réponse
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                return json.loads(response)
            except json.JSONDecodeError:
                return self._get_default_insights()
        
        return self._get_default_insights()
    
    def analyser_tendances(self, entrees_textes: List[str]) -> Dict:
        """
        Analyse les tendances sur plusieurs entrées
        
        Args:
            entrees_textes: Liste des textes des dernières entrées
            
        Returns:
            Dict avec tendances émotionnelles, thèmes récurrents
        """
        # Limiter à 10 entrées max pour ne pas dépasser les tokens
        textes_combines = "\n\n---\n\n".join(entrees_textes[:10])
        
        messages = [
            {
                "role": "system",
                "content": """Tu es un analyste de données émotionnelles. Analyse ces entrées de journal et identifie les tendances.
                Retourne un JSON avec:
                {
                    "tendance_emotionnelle": "description de l'évolution émotionnelle",
                    "themes_recurrents": ["thème1", "thème2", "thème3"],
                    "evolution": "positive/stable/negative",
                    "recommandations": ["recommandation1", "recommandation2"]
                }
                Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire."""
            },
            {
                "role": "user",
                "content": f"Entrées de journal (les plus récentes):\n\n{textes_combines[:3000]}"
            }
        ]
        
        response = self._call_groq(messages, temperature=0.5, max_tokens=600)
        
        if response:
            try:
                # Nettoyer la réponse
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                return json.loads(response)
            except json.JSONDecodeError:
                return self._get_default_trends()
        
        return self._get_default_trends()
    
    def generer_prompt_ecriture(self, contexte: str = "") -> str:
        """
        Génère un prompt d'écriture personnalisé
        
        Args:
            contexte: Contexte optionnel (humeur, thème souhaité, etc.)
            
        Returns:
            Prompt d'écriture inspirant
        """
        contexte_msg = f"\nContexte: {contexte}" if contexte else ""
        
        messages = [
            {
                "role": "system",
                "content": f"""Tu es un coach d'écriture créatif. Génère un prompt d'écriture inspirant pour un journal intime.
                Le prompt doit:
                - Être une question ou une invitation à réfléchir
                - Encourager l'introspection
                - Être bienveillant et positif
                {contexte_msg}
                
                Réponds directement avec le prompt, sans introduction."""
            },
            {
                "role": "user",
                "content": "Génère un prompt d'écriture pour aujourd'hui."
            }
        ]
        
        response = self._call_groq(messages, temperature=0.8, max_tokens=150)
        return response if response else "Qu'est-ce qui vous a fait sourire aujourd'hui ?"
    
    def chatbot_conversation(self, question: str, contexte_journal: str = "", historique: List[Dict] = None) -> str:
        """
        Chatbot conversationnel pour discuter du journal
        
        Args:
            question: Question de l'utilisateur
            contexte_journal: Contexte des entrées récentes (optionnel)
            historique: Historique de conversation (optionnel)
            
        Returns:
            Réponse du chatbot
        """
        # Construire les messages avec historique
        messages = [
            {
                "role": "system",
                "content": f"""Tu es un assistant bienveillant et empathique spécialisé dans le journaling et le développement personnel.
                
                Ton rôle:
                - Aider l'utilisateur à réfléchir sur ses entrées de journal
                - Poser des questions pertinentes pour approfondir
                - Donner des conseils constructifs et bienveillants
                - Encourager la pratique du journaling
                - Être à l'écoute et respectueux
                
                Style de réponse:
                - Chaleureux et encourageant
                - Concis (2-4 phrases maximum)
                - Utilise des emojis avec modération
                - Pose des questions ouvertes quand approprié
                
                {f"Contexte du journal de l'utilisateur: {contexte_journal[:1000]}" if contexte_journal else ""}
                
                Réponds directement à la question, sans formule de politesse excessive."""
            }
        ]
        
        # Ajouter l'historique si présent
        if historique:
            for msg in historique[-10:]:  # Garder les 10 derniers messages
                messages.append(msg)
        
        # Ajouter la question actuelle
        messages.append({
            "role": "user",
            "content": question
        })
        
        response = self._call_groq(messages, temperature=0.7, max_tokens=300)
        return response if response else "Je suis désolé, je n'ai pas pu traiter votre question. Pourriez-vous reformuler ?"
    
    def chatbot_analyser_entree(self, entree_texte: str, question: str) -> str:
        """
        Répond à une question spécifique sur une entrée de journal
        
        Args:
            entree_texte: Contenu de l'entrée
            question: Question de l'utilisateur
            
        Returns:
            Réponse basée sur l'entrée
        """
        messages = [
            {
                "role": "system",
                "content": """Tu es un analyste de journal intime bienveillant. 
                Réponds aux questions sur l'entrée de journal de manière:
                - Perspicace et réfléchie
                - Bienveillante et encourageante
                - Concise (2-3 phrases)
                - Basée sur le contenu fourni
                
                Réponds directement à la question."""
            },
            {
                "role": "user",
                "content": f"Entrée de journal:\n{entree_texte[:2000]}\n\nQuestion: {question}"
            }
        ]
        
        response = self._call_groq(messages, temperature=0.6, max_tokens=250)
        return response if response else "Je ne peux pas répondre à cette question pour le moment."
    
    def chatbot_suggestions_questions(self, entree_texte: str) -> List[str]:
        """
        Génère des questions de réflexion basées sur une entrée
        
        Args:
            entree_texte: Contenu de l'entrée
            
        Returns:
            Liste de questions suggérées
        """
        messages = [
            {
                "role": "system",
                "content": """Tu es un coach de développement personnel. 
                Génère 3 questions de réflexion pertinentes basées sur l'entrée de journal.
                
                Les questions doivent:
                - Encourager l'introspection
                - Être ouvertes (pas oui/non)
                - Être bienveillantes
                - Aider à approfondir la réflexion
                
                Retourne un JSON simple: ["question1", "question2", "question3"]
                Réponds UNIQUEMENT avec le JSON."""
            },
            {
                "role": "user",
                "content": f"Entrée:\n{entree_texte[:1500]}"
            }
        ]
        
        response = self._call_groq(messages, temperature=0.7, max_tokens=300)
        
        if response:
            try:
                # Nettoyer la réponse
                response = response.strip()
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()
                
                questions = json.loads(response)
                return questions[:3]
            except json.JSONDecodeError:
                return [
                    "Qu'avez-vous ressenti en écrivant cette entrée ?",
                    "Que pourriez-vous faire différemment ?",
                    "Qu'avez-vous appris de cette expérience ?"
                ]
        
        return [
            "Qu'avez-vous ressenti en écrivant cette entrée ?",
            "Que pourriez-vous faire différemment ?",
            "Qu'avez-vous appris de cette expérience ?"
        ]
    
    # Méthodes utilitaires pour valeurs par défaut
    
    def _get_default_emotion_analysis(self) -> Dict:
        """Retourne une analyse émotionnelle par défaut"""
        return {
            "emotions_principales": ["Neutre"],
            "sentiment_score": 0.5,
            "themes": ["Réflexion personnelle"],
            "intensite_emotionnelle": "moyenne",
            "resume_emotionnel": "Entrée de journal"
        }
    
    def _get_default_insights(self) -> Dict:
        """Retourne des insights par défaut"""
        return {
            "observation_principale": "Merci d'avoir partagé vos pensées",
            "patterns_detectes": [],
            "suggestions": ["Continuez à écrire régulièrement"],
            "questions_reflexion": ["Que pourriez-vous faire différemment demain ?"]
        }
    
    def _get_default_trends(self) -> Dict:
        """Retourne des tendances par défaut"""
        return {
            "tendance_emotionnelle": "Évolution stable",
            "themes_recurrents": [],
            "evolution": "stable",
            "recommandations": ["Continuez à tenir votre journal"]
        }


# Instance globale du service (singleton)
_ai_service_instance = None

def get_ai_service() -> GroqAIService:
    """
    Retourne l'instance unique du service AI
    
    Returns:
        Instance de GroqAIService
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = GroqAIService()
    return _ai_service_instance
