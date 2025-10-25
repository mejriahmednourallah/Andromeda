"""
Vues pour les fonctionnalités d'Intelligence Artificielle
Utilise Groq API pour l'analyse avancée du journal
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import EntreeJournal, Tag
from .services.ai_service import get_ai_service


@login_required
@require_http_methods(["POST"])
def analyser_entree_ai(request, pk):
    """
    Analyse une entrée de journal avec l'IA Groq
    
    Retourne:
        - Analyse émotionnelle
        - Tags suggérés
        - Résumé
        - Insights
    """
    entree = get_object_or_404(EntreeJournal, pk=pk, utilisateur=request.user)
    
    try:
        ai_service = get_ai_service()
        
        # Analyse émotionnelle
        emotions = ai_service.analyser_emotions(entree.contenu_texte)
        
        # Suggestions de tags
        tags_existants = list(Tag.objects.filter(utilisateur=request.user).values_list('nom', flat=True))
        tags_suggeres = ai_service.suggerer_tags(entree.contenu_texte, tags_existants)
        
        # Résumé
        resume = ai_service.generer_resume(entree.contenu_texte, longueur="court")
        
        # Insights
        insights = ai_service.generer_insights(entree.contenu_texte)
        
        return JsonResponse({
            'success': True,
            'analyse': {
                'emotions': emotions,
                'tags_suggeres': tags_suggeres,
                'resume': resume,
                'insights': insights
            }
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': 'Clé API Groq non configurée. Veuillez ajouter GROQ_API_KEY dans votre fichier .env'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de l\'analyse: {str(e)}'
        }, status=500)


@login_required
def analyse_tendances_ai(request):
    """
    Analyse les tendances émotionnelles sur les dernières entrées
    """
    # Récupérer les 10 dernières entrées
    entrees = EntreeJournal.objects.filter(
        utilisateur=request.user
    ).order_by('-date_creation')[:10]
    
    if not entrees:
        return JsonResponse({
            'success': False,
            'error': 'Aucune entrée trouvée'
        })
    
    try:
        ai_service = get_ai_service()
        
        # Extraire les textes
        textes = [entree.contenu_texte for entree in entrees]
        
        # Analyser les tendances
        tendances = ai_service.analyser_tendances(textes)
        
        return JsonResponse({
            'success': True,
            'tendances': tendances,
            'nombre_entrees_analysees': len(entrees)
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': 'Clé API Groq non configurée'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }, status=500)


@login_required
def generer_prompt_ai(request):
    """
    Génère un prompt d'écriture personnalisé
    """
    contexte = request.GET.get('contexte', '')
    
    try:
        ai_service = get_ai_service()
        prompt = ai_service.generer_prompt_ecriture(contexte)
        
        return JsonResponse({
            'success': True,
            'prompt': prompt
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': 'Clé API Groq non configurée'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }, status=500)


@login_required
def page_analyse_ai(request):
    """
    Page dédiée à l'analyse IA du journal
    """
    # Récupérer quelques statistiques pour la page
    total_entrees = EntreeJournal.objects.filter(utilisateur=request.user).count()
    
    # Dernières entrées pour l'analyse
    dernieres_entrees = EntreeJournal.objects.filter(
        utilisateur=request.user
    ).order_by('-date_creation')[:5]
    
    context = {
        'total_entrees': total_entrees,
        'dernieres_entrees': dernieres_entrees,
    }
    
    return render(request, 'core/journal/analyse_ai.html', context)


@login_required
@require_http_methods(["POST"])
def appliquer_tags_suggeres(request, pk):
    """
    Applique les tags suggérés par l'IA à une entrée
    """
    entree = get_object_or_404(EntreeJournal, pk=pk, utilisateur=request.user)
    
    try:
        data = json.loads(request.body)
        tags_noms = data.get('tags', [])
        
        # Créer ou récupérer les tags et les associer à l'entrée
        for tag_nom in tags_noms:
            tag, created = Tag.objects.get_or_create(
                nom=tag_nom,
                utilisateur=request.user,
                defaults={'couleur': '#667eea'}  # Couleur par défaut
            )
            entree.tags.add(tag)
        
        return JsonResponse({
            'success': True,
            'message': f'{len(tags_noms)} tag(s) ajouté(s)'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }, status=500)


# ===== CHATBOT =====

@login_required
def page_chatbot(request):
    """
    Page du chatbot conversationnel
    """
    # Récupérer les dernières entrées pour le contexte
    entrees_recentes = EntreeJournal.objects.filter(
        utilisateur=request.user
    ).order_by('-date_creation')[:5]
    
    context = {
        'entrees_recentes': entrees_recentes,
    }
    
    return render(request, 'core/journal/chatbot.html', context)


@login_required
@require_http_methods(["POST"])
def chatbot_message(request):
    """
    Traite un message du chatbot
    """
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        historique = data.get('historique', [])
        entree_id = data.get('entree_id')
        
        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Question vide'
            })
        
        ai_service = get_ai_service()
        
        # Si une entrée spécifique est sélectionnée
        if entree_id:
            entree = get_object_or_404(EntreeJournal, pk=entree_id, utilisateur=request.user)
            reponse = ai_service.chatbot_analyser_entree(entree.contenu_texte, question)
        else:
            # Conversation générale avec contexte des entrées récentes
            entrees = EntreeJournal.objects.filter(
                utilisateur=request.user
            ).order_by('-date_creation')[:3]
            
            contexte = "\n\n".join([
                f"Entrée du {e.date_creation.strftime('%d/%m/%Y')}: {e.contenu_texte[:200]}..."
                for e in entrees
            ]) if entrees else ""
            
            reponse = ai_service.chatbot_conversation(question, contexte, historique)
        
        return JsonResponse({
            'success': True,
            'reponse': reponse
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': 'Clé API Groq non configurée'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def chatbot_questions_suggerees(request, pk):
    """
    Génère des questions suggérées pour une entrée
    """
    entree = get_object_or_404(EntreeJournal, pk=pk, utilisateur=request.user)
    
    try:
        ai_service = get_ai_service()
        questions = ai_service.chatbot_suggestions_questions(entree.contenu_texte)
        
        return JsonResponse({
            'success': True,
            'questions': questions
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': 'Clé API Groq non configurée'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }, status=500)
