"""
Vues pour la gestion des entrées de journal
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.template.loader import render_to_string
from io import BytesIO
import json

from .models import EntreeJournal, Tag, Humeur, EntreeTag, EntreeHumeur
from .forms import EntreeJournalForm, TagForm
from .services.ai_service import get_ai_service

# Import for PDF generation
try:
    from xhtml2pdf import pisa
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Import for AI analysis
try:
    import openai
    from django.conf import settings
    AI_AVAILABLE = hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY
except ImportError:
    AI_AVAILABLE = False


@login_required
def liste_entrees_journal(request):
    """
    Liste toutes les entrées de journal de l'utilisateur avec filtrage
    """
    entrees = EntreeJournal.objects.filter(utilisateur=request.user).order_by('-date_creation')
    
    # Filtrage par tag
    tag_id = request.GET.get('tag')
    if tag_id:
        entrees = entrees.filter(entree_tags__tag_id=tag_id)
    
    # Filtrage par humeur
    humeur_id = request.GET.get('humeur')
    if humeur_id:
        entrees = entrees.filter(entree_humeurs__humeur_id=humeur_id)
    
    # Filtrage par favoris
    if request.GET.get('favorites') == 'true':
        entrees = entrees.filter(is_favorite=True)
    
    # Recherche
    query = request.GET.get('q')
    if query:
        entrees = entrees.filter(
            Q(titre__icontains=query) | 
            Q(contenu_texte__icontains=query) |
            Q(lieu__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(entrees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Récupérer les tags et humeurs pour les filtres
    user_tags = Tag.objects.filter(
        Q(utilisateur=request.user) | Q(utilisateur__isnull=True)
    ).order_by('nom')
    humeurs = Humeur.objects.all().order_by('nom')
    
    context = {
        'page_obj': page_obj,
        'entrees': page_obj.object_list,
        'user_tags': user_tags,
        'humeurs': humeurs,
        'query': query,
        'selected_tag': tag_id,
        'selected_humeur': humeur_id,
    }
    
    return render(request, 'core/journal/liste_entrees.html', context)


@login_required
def detail_entree_journal(request, pk):
    """
    Affiche les détails d'une entrée de journal
    """
    entree = get_object_or_404(EntreeJournal, pk=pk, utilisateur=request.user)
    
    context = {
        'entree': entree,
        'tags': entree.tags_list,
        'humeurs': entree.humeurs_list,
    }
    
    return render(request, 'core/journal/detail_entree.html', context)


@login_required
def ajouter_entree_journal(request):
    """
    Créer une nouvelle entrée de journal
    """
    if request.method == 'POST':
        form = EntreeJournalForm(request.POST, user=request.user)
        if form.is_valid():
            entree = form.save(commit=False)
            entree.utilisateur = request.user
            entree.save()
            
            # Sauvegarder les tags
            tags = form.cleaned_data.get('tags')
            if tags:
                for tag in tags:
                    EntreeTag.objects.create(entree_journal=entree, tag=tag)
            
            # Sauvegarder les humeurs avec intensité par défaut
            humeurs = form.cleaned_data.get('humeurs')
            if humeurs:
                for humeur in humeurs:
                    EntreeHumeur.objects.create(
                        entree_journal=entree, 
                        humeur=humeur,
                        intensite=3  # Intensité moyenne par défaut
                    )
            
            # Générer le résumé automatique avec l'IA
            try:
                ai_service = get_ai_service()
                resume = ai_service.generer_resume(entree.contenu_texte, longueur="court")
                entree.auto_summary = resume
                entree.save()
            except Exception as e:
                # Si l'IA échoue, continuer sans résumé
                print(f"Erreur génération résumé: {e}")
            
            messages.success(request, 'Entrée de journal créée avec succès!')
            return redirect('core:detail_entree_journal', pk=entree.pk)
    else:
        form = EntreeJournalForm(user=request.user)
    
    context = {
        'form': form,
        'action': 'Créer',
    }
    
    return render(request, 'core/journal/form_entree.html', context)


@login_required
def modifier_entree_journal(request, pk):
    """
    Modifier une entrée de journal existante
    """
    entree = get_object_or_404(EntreeJournal, pk=pk, utilisateur=request.user)
    
    if request.method == 'POST':
        form = EntreeJournalForm(request.POST, instance=entree, user=request.user)
        if form.is_valid():
            entree = form.save()
            
            # Mettre à jour les tags
            EntreeTag.objects.filter(entree_journal=entree).delete()
            tags = form.cleaned_data.get('tags')
            if tags:
                for tag in tags:
                    EntreeTag.objects.create(entree_journal=entree, tag=tag)
            
            # Mettre à jour les humeurs
            EntreeHumeur.objects.filter(entree_journal=entree).delete()
            humeurs = form.cleaned_data.get('humeurs')
            if humeurs:
                for humeur in humeurs:
                    EntreeHumeur.objects.create(
                        entree_journal=entree,
                        humeur=humeur,
                        intensite=3
                    )
            
            messages.success(request, 'Entrée de journal modifiée avec succès!')
            return redirect('core:detail_entree_journal', pk=entree.pk)
    else:
        form = EntreeJournalForm(instance=entree, user=request.user)
    
    context = {
        'form': form,
        'entree': entree,
        'action': 'Modifier',
    }
    
    return render(request, 'core/journal/form_entree.html', context)


@login_required
def supprimer_entree_journal(request, pk):
    """
    Supprimer une entrée de journal
    """
    entree = get_object_or_404(EntreeJournal, pk=pk, utilisateur=request.user)
    
    if request.method == 'POST':
        entree.delete()
        messages.success(request, 'Entrée de journal supprimée avec succès!')
        return redirect('core:liste_entrees_journal')
    
    context = {
        'entree': entree,
    }
    
    return render(request, 'core/journal/confirmer_suppression.html', context)


@login_required
def toggle_favori_entree(request, pk):
    """
    Basculer le statut favori d'une entrée (AJAX)
    """
    if request.method == 'POST':
        entree = get_object_or_404(EntreeJournal, pk=pk, utilisateur=request.user)
        entree.is_favorite = not entree.is_favorite
        entree.save()
        
        return JsonResponse({
            'success': True,
            'is_favorite': entree.is_favorite
        })
    
    return JsonResponse({'success': False}, status=400)


# ===== Gestion des Tags =====

@login_required
def liste_tags(request):
    """
    Liste tous les tags de l'utilisateur
    """
    tags = Tag.objects.filter(
        Q(utilisateur=request.user) | Q(utilisateur__isnull=True)
    ).annotate(
        nb_entrees=Count('entree_tags')
    ).order_by('nom')
    
    context = {
        'tags': tags,
    }
    
    return render(request, 'core/journal/liste_tags.html', context)


@login_required
def ajouter_tag(request):
    """
    Créer un nouveau tag
    """
    if request.method == 'POST':
        form = TagForm(request.POST, user=request.user)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.utilisateur = request.user
            tag.save()
            
            messages.success(request, f'Tag "{tag.nom}" créé avec succès!')
            return redirect('core:liste_tags')
    else:
        form = TagForm(user=request.user)
    
    context = {
        'form': form,
        'action': 'Créer',
    }
    
    return render(request, 'core/journal/form_tag.html', context)


@login_required
def modifier_tag(request, pk):
    """
    Modifier un tag existant
    """
    tag = get_object_or_404(Tag, pk=pk, utilisateur=request.user)
    
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tag "{tag.nom}" modifié avec succès!')
            return redirect('core:liste_tags')
    else:
        form = TagForm(instance=tag, user=request.user)
    
    context = {
        'form': form,
        'tag': tag,
        'action': 'Modifier',
    }
    
    return render(request, 'core/journal/form_tag.html', context)


@login_required
def supprimer_tag(request, pk):
    """
    Supprimer un tag
    """
    tag = get_object_or_404(Tag, pk=pk, utilisateur=request.user)
    
    if request.method == 'POST':
        nom = tag.nom
        tag.delete()
        messages.success(request, f'Tag "{nom}" supprimé avec succès!')
        return redirect('core:liste_tags')
    
    context = {
        'tag': tag,
    }
    
    return render(request, 'core/journal/confirmer_suppression_tag.html', context)


# ===== Statistiques =====

@login_required
def statistiques_journal(request):
    """
    Affiche les statistiques du journal de l'utilisateur
    """
    from datetime import timedelta
    from django.utils import timezone
    
    entrees = EntreeJournal.objects.filter(utilisateur=request.user)
    
    # Statistiques générales
    total_entrees = entrees.count()
    total_mots = sum(entree.nombre_mots for entree in entrees)
    entrees_favorites = entrees.filter(is_favorite=True).count()
    moyenne_mots = round(total_mots / total_entrees) if total_entrees > 0 else 0
    
    # Calcul de la série d'écriture (writing streak)
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    if total_entrees > 0:
        # Obtenir toutes les dates uniques d'entrées, triées
        dates_entrees = entrees.values_list('date_creation__date', flat=True).distinct().order_by('-date_creation__date')
        dates_list = list(dates_entrees)
        
        if dates_list:
            # Calculer la série actuelle
            today = timezone.now().date()
            yesterday = today - timedelta(days=1)
            
            if dates_list[0] == today or dates_list[0] == yesterday:
                current_streak = 1
                last_date = dates_list[0]
                
                for date in dates_list[1:]:
                    if (last_date - date).days == 1:
                        current_streak += 1
                        last_date = date
                    else:
                        break
            
            # Calculer la série la plus longue
            temp_streak = 1
            longest_streak = 1
            last_date = dates_list[0]
            
            for date in dates_list[1:]:
                if (last_date - date).days == 1:
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 1
                last_date = date
    
    # Tags les plus utilisés
    tags_populaires = Tag.objects.filter(
        entree_tags__entree_journal__utilisateur=request.user
    ).annotate(
        nb_utilisations=Count('entree_tags')
    ).order_by('-nb_utilisations')[:10]
    
    # Humeurs les plus fréquentes
    humeurs_frequentes = Humeur.objects.filter(
        entree_humeurs__entree_journal__utilisateur=request.user
    ).annotate(
        nb_utilisations=Count('entree_humeurs')
    ).order_by('-nb_utilisations')[:10]
    
    # Entrées récentes
    entrees_recentes = entrees.order_by('-date_creation')[:5]
    
    # Données pour le graphique d'évolution temporelle (30 derniers jours)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    entrees_recentes_30j = entrees.filter(date_creation__gte=thirty_days_ago).order_by('date_creation')
    
    # Préparer les données pour le graphique
    timeline_data = []
    for i in range(30):
        date = (timezone.now() - timedelta(days=29-i)).date()
        entries_on_date = entrees_recentes_30j.filter(date_creation__date=date)
        
        # Compter les humeurs positives vs négatives
        positive_moods = ['Joyeux', 'Excité', 'Calme', 'Reconnaissant', 'Inspiré']
        negative_moods = ['Triste', 'Anxieux', 'En colère', 'Frustré', 'Fatigué']
        
        positive_count = 0
        negative_count = 0
        
        for entry in entries_on_date:
            humeurs = [eh.humeur.nom for eh in entry.entree_humeurs.all()]
            positive_count += sum(1 for h in humeurs if h in positive_moods)
            negative_count += sum(1 for h in humeurs if h in negative_moods)
        
        timeline_data.append({
            'date': date.strftime('%d/%m'),
            'positive': positive_count,
            'negative': negative_count,
            'entries': entries_on_date.count()
        })
    
    context = {
        'total_entrees': total_entrees,
        'total_mots': total_mots,
        'entrees_favorites': entrees_favorites,
        'moyenne_mots': moyenne_mots,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'tags_populaires': tags_populaires,
        'humeurs_frequentes': humeurs_frequentes,
        'entrees_recentes': entrees_recentes,
        'timeline_data': timeline_data,
    }
    
    return render(request, 'core/journal/statistiques.html', context)


# ===== Export PDF =====

@login_required
def export_journal_pdf(request):
    """
    Exporte toutes les entrées de journal en PDF
    """
    if not PDF_AVAILABLE:
        messages.error(request, 'Export PDF non disponible. Veuillez installer xhtml2pdf.')
        return redirect('core:statistiques_journal')
    
    entrees = EntreeJournal.objects.filter(utilisateur=request.user).order_by('-date_creation')
    
    # Préparer le contexte pour le template
    context = {
        'entrees': entrees,
        'user': request.user,
        'date_export': timezone.now(),
        'total_entrees': entrees.count(),
        'total_mots': sum(e.nombre_mots for e in entrees),
    }
    
    # Générer le HTML
    html_string = render_to_string('core/journal/pdf_template.html', context)
    
    # Créer le PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="mon-journal-{timezone.now().strftime("%Y-%m-%d")}.pdf"'
        return response
    
    messages.error(request, 'Erreur lors de la génération du PDF.')
    return redirect('core:statistiques_journal')


@login_required
def export_entree_pdf(request, pk):
    """
    Exporte une seule entrée en PDF
    """
    if not PDF_AVAILABLE:
        messages.error(request, 'Export PDF non disponible.')
        return redirect('core:detail_entree_journal', pk=pk)
    
    entree = get_object_or_404(EntreeJournal, pk=pk, utilisateur=request.user)
    
    context = {
        'entree': entree,
        'tags': entree.tags_list,
        'humeurs': entree.humeurs_list,
        'date_export': timezone.now(),
    }
    
    html_string = render_to_string('core/journal/pdf_entree_template.html', context)
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="entree-{entree.pk}.pdf"'
        return response
    
    messages.error(request, 'Erreur lors de la génération du PDF.')
    return redirect('core:detail_entree_journal', pk=pk)


# ===== Analyse IA =====

@login_required
def analyser_entree_ia(request):
    """
    Analyse une entrée de journal avec l'IA
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        titre = data.get('titre', '')
        contenu = data.get('contenu', '')
        
        if not contenu or len(contenu.strip()) < 10:
            return JsonResponse({'error': 'Contenu trop court'}, status=400)
        
        # Analyse IA ou simulation
        if AI_AVAILABLE:
            result = _analyze_with_openai(titre, contenu)
        else:
            result = _simulate_ai_analysis(titre, contenu)
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _analyze_with_openai(titre, contenu):
    """
    Analyse avec OpenAI GPT
    """
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = f"""Analyse cette entrée de journal et fournis:
1. L'émotion principale (joyeux, triste, anxieux, calme, etc.)
2. Un score de confiance pour l'émotion (0-1)
3. 3-5 tags pertinents
4. Un résumé en une phrase

Titre: {titre}
Contenu: {contenu}

Réponds au format JSON avec les clés: emotion, emotion_score, suggested_tags (liste), summary"""
        
        response = client.chat.completions.create(
            model=settings.AI_TEXT_MODEL if hasattr(settings, 'AI_TEXT_MODEL') else 'gpt-4o-mini',
            messages=[
                {"role": "system", "content": "Tu es un assistant qui analyse des entrées de journal."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        return _simulate_ai_analysis(titre, contenu)


def _simulate_ai_analysis(titre, contenu):
    """
    Simulation d'analyse IA (fallback)
    """
    # Détection simple d'émotions par mots-clés
    contenu_lower = contenu.lower()
    
    emotions = {
        'joyeux': ['heureux', 'joie', 'content', 'ravi', 'super', 'génial', 'excellent'],
        'triste': ['triste', 'malheureux', 'déprimé', 'mélancolique', 'peine'],
        'anxieux': ['anxieux', 'inquiet', 'stress', 'peur', 'angoisse', 'nerveux'],
        'calme': ['calme', 'paisible', 'serein', 'tranquille', 'relaxé'],
        'excité': ['excité', 'enthousiaste', 'motivé', 'énergique'],
        'en colère': ['colère', 'énervé', 'furieux', 'irrité', 'frustré'],
    }
    
    detected_emotion = 'neutre'
    max_score = 0
    
    for emotion, keywords in emotions.items():
        score = sum(1 for keyword in keywords if keyword in contenu_lower)
        if score > max_score:
            max_score = score
            detected_emotion = emotion
    
    # Extraction de tags simples
    words = contenu_lower.split()
    common_tags = ['travail', 'famille', 'amis', 'voyage', 'santé', 'projet', 'lecture', 'sport']
    suggested_tags = [tag for tag in common_tags if tag in contenu_lower][:5]
    
    # Résumé simple (première phrase)
    sentences = contenu.split('.')
    summary = sentences[0][:100] + '...' if sentences else contenu[:100] + '...'
    
    return {
        'emotion': detected_emotion,
        'emotion_score': min(0.5 + (max_score * 0.1), 0.95),
        'suggested_tags': suggested_tags if suggested_tags else ['personnel', 'réflexion'],
        'summary': summary
    }
