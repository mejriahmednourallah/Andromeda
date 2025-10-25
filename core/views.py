from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
import logging
from io import BytesIO

from .models import (
    Note, User, Souvenir, AnalyseIASouvenir, AlbumSouvenir,
    CapsuleTemporelle, PartageSouvenir, SuiviMotivationnel, ExportPDF
)
from .forms import UserCreationForm, SouvenirForm, CapsuleTemporelleForm, UserProfileForm
from .ai_services import AIAnalysisService, AIRecommendationService

logger = logging.getLogger(__name__)

def ensure_sample_notes():
    """Create sample notes for demo if database is empty"""
    if Note.objects.exists():
        return
    
    # Get or create demo user
    user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'first_name': 'Bruce',
            'last_name': 'Wayne'
        }
    )
    if created:
        user.set_password('demo')
        user.save()

    # Create sample notes
    samples = [
        ('The Great Gatsby', 'A classic novel card — demo content.'),
        ('One Hundred Years of Solitude', 'Magical realist note star.'),
        ('To Kill a Mockingbird', 'A note about justice and growth.'),
        ('Of Human Bondage', 'Classic literature sample.'),
        ('Breaking Dawn', 'Popular fiction example.'),
    ]
    Note.objects.bulk_create([
        Note(owner=user, title=title, body=body)
        for title, body in samples
    ])

def index(request):
    ensure_sample_notes()
    notes = Note.objects.all().order_by('-created_at')[:20]
    return render(request, 'core/index.html', {'notes': notes})

def note_detail(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    return render(request, 'core/note_detail.html', {'note': note})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})


@login_required
def dashboard(request):
    """
    Vue principale du dashboard avec statistiques et activités récentes.
    """
    # Statistiques
    notes_count = Note.objects.filter(owner=request.user).count()
    souvenirs_count = Souvenir.objects.filter(utilisateur=request.user).count()
    
    # Activités récentes
    recent_souvenirs = Souvenir.objects.filter(utilisateur=request.user).order_by('-created_at')[:6]
    recent_notes = Note.objects.filter(owner=request.user).order_by('-created_at')[:5]
    
    context = {
        'notes_count': notes_count,
        'souvenirs_count': souvenirs_count,
        'recent_souvenirs': recent_souvenirs,
        'recent_notes': recent_notes,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def profile(request):
    """
    User profile management view
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Profile updated successfully!')
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=request.user)

    # User statistics
    user_stats = {
        'total_memories': Souvenir.objects.filter(utilisateur=request.user).count(),
        'favorite_memories': Souvenir.objects.filter(utilisateur=request.user, is_favorite=True).count(),
        'analyzed_memories': Souvenir.objects.filter(utilisateur=request.user, ai_analyzed=True).count(),
        'albums_count': AlbumSouvenir.objects.filter(utilisateur=request.user).count(),
        'capsules_count': CapsuleTemporelle.objects.filter(souvenir__utilisateur=request.user).count(),
        'notes_count': Note.objects.filter(owner=request.user).count(),
        'member_since': request.user.date_joined.strftime('%B %Y'),
    }

    # Recent activity
    recent_activity = []

    # Recent memories
    recent_memories = Souvenir.objects.filter(utilisateur=request.user).order_by('-created_at')[:3]
    for memory in recent_memories:
        recent_activity.append({
            'type': 'memory',
            'title': f'Created memory "{memory.titre}"',
            'date': memory.created_at,
            'url': reverse('core:detail_souvenir', args=[memory.id])
        })

    # Recent capsules
    recent_capsules = CapsuleTemporelle.objects.filter(souvenir__utilisateur=request.user).order_by('-date_verrouillage')[:2]
    for capsule in recent_capsules:
        recent_activity.append({
            'type': 'capsule',
            'title': f'Created time capsule "{capsule.souvenir.titre}"',
            'date': capsule.date_verrouillage,
            'url': reverse('core:detail_capsule', args=[capsule.id])
        })

    # Sort by date and take top 5
    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    recent_activity = recent_activity[:5]

    context = {
        'form': form,
        'user_stats': user_stats,
        'recent_activity': recent_activity,
    }

    return render(request, 'core/profile.html', context)


@login_required
def ajouter_souvenir(request):
    """
    Vue pour ajouter un souvenir dans la base de données.
    Nécessite que l'utilisateur soit authentifié.
    """
    if request.method == 'POST':
        form = SouvenirForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Créer le souvenir sans le sauvegarder immédiatement
                souvenir = form.save(commit=False)
                # Associer l'utilisateur connecté
                souvenir.utilisateur = request.user
                # Sauvegarder avec validation automatique
                souvenir.save()
                
                # Perform AI analysis automatically
                try:
                    AIAnalysisService.analyze_memory(souvenir)
                    messages.success(request, f'✨ Souvenir "{souvenir.titre}" ajouté avec succès et analysé par IA!')
                except Exception as e:
                    # Don't fail souvenir creation if AI analysis fails
                    messages.success(request, f'Souvenir "{souvenir.titre}" ajouté avec succès!')
                    messages.warning(request, f'⚠️ Analyse IA non disponible: {str(e)}')
                    logger.warning(f'AI analysis failed for new memory {souvenir.id}: {str(e)}')
                
                logger.info(f'Souvenir créé: {souvenir.id} par utilisateur {request.user.username}')
                
                # Rediriger vers la liste des souvenirs
                return redirect('core:liste_souvenirs')
            
            except ValidationError as e:
                # Gérer les erreurs de validation
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
                logger.warning(f'Erreur de validation lors de la création du souvenir: {e}')
            
            except Exception as e:
                # Gérer les autres erreurs
                messages.error(request, 'Une erreur est survenue lors de l\'enregistrement du souvenir.')
                logger.error(f'Erreur lors de la création du souvenir: {str(e)}')
        else:
            # Form is invalid - errors will be displayed inline in template
            pass
    else:
        form = SouvenirForm()
    
    return render(request, 'core/ajouter_souvenir.html', {'form': form})


@login_required
def liste_souvenirs(request):
    """
    Vue pour afficher la liste des souvenirs de l'utilisateur connecté.
    """
    souvenirs = Souvenir.objects.filter(utilisateur=request.user).order_by('-date_evenement')
    return render(request, 'core/liste_souvenirs.html', {'souvenirs': souvenirs})


@login_required
def detail_souvenir(request, souvenir_id):
    """
    Vue pour afficher le détail d'un souvenir.
    Vérifie que l'utilisateur est bien le propriétaire.
    """
    souvenir = get_object_or_404(Souvenir, id=souvenir_id, utilisateur=request.user)
    return render(request, 'core/detail_souvenir.html', {'souvenir': souvenir})


@login_required
def supprimer_souvenir(request, souvenir_id):
    """
    Delete a memory.
    Verify that the user is the owner.
    """
    souvenir = get_object_or_404(Souvenir, id=souvenir_id, utilisateur=request.user)
    
    if request.method == 'POST':
        titre = souvenir.titre
        souvenir.delete()
        messages.success(request, f'Memory "{titre}" successfully deleted.')
        logger.info(f'Memory {souvenir_id} deleted by {request.user.username}')
        return redirect('core:liste_souvenirs')
    
    return render(request, 'core/supprimer_souvenir.html', {'souvenir': souvenir})


# ============================================
# NEW VIEWS: COMPLETE CRUD + AI FEATURES
# ============================================

@login_required
def modifier_souvenir(request, souvenir_id):
    """
    Edit an existing memory
    """
    souvenir = get_object_or_404(Souvenir, id=souvenir_id, utilisateur=request.user)
    
    if request.method == 'POST':
        form = SouvenirForm(request.POST, request.FILES, instance=souvenir)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'✅ Memory "{souvenir.titre}" updated successfully!')
                logger.info(f'Memory {souvenir_id} updated by {request.user.username}')
                return redirect('core:detail_souvenir', souvenir_id=souvenir.id)
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
        else:
            # Form is invalid - errors will be displayed inline in template
            pass
    else:
        form = SouvenirForm(instance=souvenir)
    
    return render(request, 'core/modifier_souvenir.html', {
        'form': form,
        'souvenir': souvenir
    })


@login_required
def memories_dashboard(request):
    """
    Unified Memories Dashboard: Combines My Memories and AI Gallery
    """
    # Get base souvenirs queryset
    souvenirs = Souvenir.objects.filter(utilisateur=request.user)

    # Apply filters from GET parameters
    emotion = request.GET.get('emotion')
    theme = request.GET.get('theme')
    annee = request.GET.get('annee')
    favoris_only = request.GET.get('favoris')
    search_query = request.GET.get('q')
    ai_status = request.GET.get('ai_status')  # 'analyzed', 'pending', or None

    filtered_souvenirs = souvenirs

    # Apply filters
    if emotion:
        filtered_souvenirs = filtered_souvenirs.filter(emotion=emotion)
    if theme:
        filtered_souvenirs = filtered_souvenirs.filter(theme=theme)
    if annee:
        filtered_souvenirs = filtered_souvenirs.filter(date_evenement__year=annee)
    if favoris_only:
        filtered_souvenirs = filtered_souvenirs.filter(is_favorite=True)
    if search_query:
        # Recherche full-text étendue
        filtered_souvenirs = filtered_souvenirs.filter(
            Q(titre__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(lieu__icontains=search_query) |
            Q(personnes_presentes__icontains=search_query) |
            Q(ai_tags__icontains=search_query)
        )
    if ai_status == 'analyzed':
        filtered_souvenirs = filtered_souvenirs.filter(ai_analyzed=True)
    elif ai_status == 'pending':
        filtered_souvenirs = filtered_souvenirs.filter(ai_analyzed=False)

    # Separate analyzed and pending for display
    analyzed_souvenirs = filtered_souvenirs.filter(ai_analyzed=True)
    pending_souvenirs = filtered_souvenirs.filter(ai_analyzed=False)

    # Get AI insights
    insights = AIRecommendationService.get_memory_insights(request.user)

    # Album suggestions
    album_suggestions = AIAnalysisService.generate_album_suggestions(request.user)
    
    # Add souvenir IDs to suggestions for pre-selection
    for suggestion in album_suggestions:
        suggestion['souvenir_ids'] = AIAnalysisService.get_souvenir_ids_for_suggestion(request.user, suggestion['type'], suggestion.get('theme'), suggestion.get('year'))

    # Reflection prompts
    reflection_prompts = AIRecommendationService.suggest_reflection_prompts(request.user)

    # Statistics
    stats = {
        'total_memories': souvenirs.count(),
        'favorites': souvenirs.filter(is_favorite=True).count(),
        'analyzed': souvenirs.filter(ai_analyzed=True).count(),
        'pending': souvenirs.filter(ai_analyzed=False).count(),
        'with_media': souvenirs.filter(photo__isnull=False).count(),
        'filtered_count': filtered_souvenirs.count(),
    }

    # Pagination for filtered results
    paginator = Paginator(filtered_souvenirs.order_by('-date_evenement'), 12)
    page = request.GET.get('page')
    souvenirs_page = paginator.get_page(page)

    # Get available years for filter
    available_years = souvenirs.dates('date_evenement', 'year', order='DESC')

    # Calculate facet counts for interactive filters
    facet_counts = {
        'emotions': {},
        'themes': {},
        'years': {},
        'ai_status': {
            'analyzed': souvenirs.filter(ai_analyzed=True).count(),
            'pending': souvenirs.filter(ai_analyzed=False).count(),
        }
    }

    # Count emotions
    for emotion_code, emotion_name in Souvenir.EMOTION_CHOICES:
        count = souvenirs.filter(emotion=emotion_code).count()
        if count > 0:
            facet_counts['emotions'][emotion_code] = {
                'name': emotion_name,
                'count': count
            }

    # Count themes
    for theme_code, theme_name in Souvenir.THEME_CHOICES:
        count = souvenirs.filter(theme=theme_code).count()
        if count > 0:
            facet_counts['themes'][theme_code] = {
                'name': theme_name,
                'count': count
            }

    # Count years
    for year in available_years:
        count = souvenirs.filter(date_evenement__year=year.year).count()
        facet_counts['years'][year.year] = count

    # Handle batch AI analysis
    if request.method == 'POST' and 'analyze_all' in request.POST:
        pending = souvenirs.filter(ai_analyzed=False)
        if not pending.exists():
            messages.info(request, 'ℹ️ No memories pending analysis')
        else:
            success_count = 0
            error_count = 0

            for souvenir in pending[:10]:  # Limit to 10 at a time
                try:
                    AIAnalysisService.analyze_memory(souvenir)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    logger.error(f'Batch analysis failed for {souvenir.id}: {str(e)}')

            if success_count > 0:
                messages.success(request, f'✨ {success_count} memories analyzed successfully!')
            if error_count > 0:
                messages.warning(request, f'⚠️ {error_count} memories failed analysis')

        return redirect('core:memories_dashboard')

    context = {
        # Statistics
        'stats': stats,
        'insights': insights,

        # Filtered and paginated memories
        'souvenirs': souvenirs_page,
        'analyzed_souvenirs': analyzed_souvenirs[:6],  # For AI section
        'pending_souvenirs': pending_souvenirs[:6],    # For pending section

        # AI Features
        'album_suggestions': album_suggestions,
        'reflection_prompts': reflection_prompts,

        # Filters
        'filtres_actifs': {
            'emotion': emotion,
            'theme': theme,
            'annee': annee,
            'favoris': favoris_only,
            'search': search_query,
            'ai_status': ai_status,
        },
        'available_years': available_years,
        'emotion_choices': Souvenir.EMOTION_CHOICES,
        'theme_choices': Souvenir.THEME_CHOICES,
        'facet_counts': facet_counts,

        # Pagination
        'paginator': paginator,
        'page_obj': souvenirs_page,
    }

    return render(request, 'core/memories_dashboard.html', context)


@login_required
def toggle_favori(request, souvenir_id):
    """
    Toggle favorite status of a memory
    """
    souvenir = get_object_or_404(Souvenir, id=souvenir_id, utilisateur=request.user)
    souvenir.is_favorite = not souvenir.is_favorite
    souvenir.save()
    
    status = "added to" if souvenir.is_favorite else "removed from"
    messages.success(request, f'⭐ Memory {status} favorites')
    
    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorite': souvenir.is_favorite,
            'message': f'Memory {status} favorites'
        })
    
    return redirect('core:detail_souvenir', souvenir_id=souvenir.id)


# ============================================
# AI ANALYSIS VIEWS
# ============================================

@login_required
def analyser_souvenir_ia(request, souvenir_id):
    """
    Analyze a memory with AI (text + image analysis)
    """
    souvenir = get_object_or_404(Souvenir, id=souvenir_id, utilisateur=request.user)
    
    # Check if already analyzed
    if hasattr(souvenir, 'analyse_ia'):
        messages.info(request, '🤖 This memory has already been analyzed by AI')
        return redirect('core:detail_souvenir', souvenir_id=souvenir.id)
    
    try:
        # Perform AI analysis
        analyse = AIAnalysisService.analyze_memory(souvenir)
        messages.success(request, '✨ Memory successfully enriched with AI analysis!')
        logger.info(f'AI analysis completed for memory {souvenir_id}')
    except Exception as e:
        messages.error(request, f'❌ Error during analysis: {str(e)}')
        logger.error(f'AI analysis failed for memory {souvenir_id}: {str(e)}')
    
    return redirect('core:detail_souvenir', souvenir_id=souvenir.id)


@login_required
def galerie_ia(request):
    """
    AI Gallery: Dashboard showing memories with AI analysis
    """
    # Get all memories
    souvenirs = Souvenir.objects.filter(utilisateur=request.user)
    
    # Separate analyzed and pending
    analyzed = souvenirs.filter(ai_analyzed=True)
    pending = souvenirs.filter(ai_analyzed=False)
    
    # Get AI insights
    insights = AIRecommendationService.get_memory_insights(request.user)
    
    # Album suggestions
    album_suggestions = AIAnalysisService.generate_album_suggestions(request.user)
    
    # Reflection prompts
    reflection_prompts = AIRecommendationService.suggest_reflection_prompts(request.user)
    
    context = {
        'analyzed_count': analyzed.count(),
        'pending_count': pending.count(),
        'analyzed_memories': analyzed[:6],
        'pending_memories': pending[:6],
        'insights': insights,
        'album_suggestions': album_suggestions,
        'reflection_prompts': reflection_prompts,
    }
    
    return render(request, 'core/galerie_ia.html', context)


@login_required
def analyser_tout_ia(request):
    """
    Batch analyze all pending memories with AI
    """
    if request.method != 'POST':
        return redirect('core:galerie_ia')
    
    pending = Souvenir.objects.filter(
        utilisateur=request.user,
        ai_analyzed=False
    )
    
    if not pending.exists():
        messages.info(request, 'ℹ️ No memories pending analysis')
        return redirect('core:galerie_ia')
    
    success_count = 0
    error_count = 0
    
    for souvenir in pending[:10]:  # Limit to 10 at a time
        try:
            AIAnalysisService.analyze_memory(souvenir)
            success_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f'Batch analysis failed for {souvenir.id}: {str(e)}')
    
    if success_count > 0:
        messages.success(request, f'✨ {success_count} memories analyzed successfully!')
    if error_count > 0:
        messages.warning(request, f'⚠️ {error_count} memories failed analysis')
    
    return redirect('core:galerie_ia')


# ============================================
# TIME CAPSULE VIEWS
# ============================================

@login_required
def generate_ai_message(request):
    """
    AJAX endpoint to generate AI message for time capsule
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get data from POST
        titre = request.POST.get('titre', '').strip()
        description = request.POST.get('description', '').strip()
        emotion = request.POST.get('emotion', 'neutral')
        
        if not titre or not description:
            return JsonResponse({'error': 'Title and description are required'}, status=400)
        
        # Create temporary souvenir object for AI analysis
        from .models import Souvenir
        temp_souvenir = Souvenir(
            titre=titre,
            description=description,
            emotion=emotion,
            utilisateur=request.user
        )
        
        # Generate AI message for time capsule
        message = AIAnalysisService.generate_time_capsule_message(temp_souvenir)
        
        return JsonResponse({
            'message': message,
            'emotion': emotion  # Keep emotion for consistency
        })
        
    except Exception as e:
        logger.error(f'Error generating AI message: {str(e)}')
        return JsonResponse({'error': 'Failed to generate AI message'}, status=500)


@login_required
def creer_capsule(request):
    """
    Create a new time capsule
    """
    if request.method == 'POST':
        form = CapsuleTemporelleForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create memory
                souvenir = form.save(commit=False)
                souvenir.utilisateur = request.user
                souvenir.save()
                
                # Perform AI analysis automatically (like in ajouter_souvenir)
                try:
                    AIAnalysisService.analyze_memory(souvenir)
                    messages.success(request, f'✨ Memory analyzed with AI!')
                except Exception as e:
                    messages.warning(request, f'⚠️ AI analysis failed: {str(e)}')
                    logger.warning(f'AI analysis failed for capsule memory {souvenir.id}: {str(e)}')
                
                # Create capsule
                message_futur = form.cleaned_data.get('message_futur', '').strip()
                
                # AI prediction
                prediction = AIAnalysisService.predict_future_emotion(souvenir)
                
                # Use AI-generated message if user didn't provide one
                if not message_futur:
                    message_futur = prediction.get('explanation', 'Welcome back to this special moment in your life.')
                
                capsule = CapsuleTemporelle.objects.create(
                    souvenir=souvenir,
                    date_ouverture=form.cleaned_data['date_ouverture'],
                    message_futur=message_futur
                )
                
                capsule.emotion_predite_par_ia = prediction['emotion']
                capsule.save()
                
                messages.success(request, f'🕰️ Time capsule created! Opens on {capsule.date_ouverture}')
                logger.info(f'Time capsule created: {capsule.id}')
                return redirect('core:liste_capsules')
                
            except Exception as e:
                messages.error(request, f'Error creating capsule: {str(e)}')
                logger.error(f'Capsule creation failed: {str(e)}')
        else:
            # Form is invalid - errors will be displayed inline in template
            pass
    else:
        form = CapsuleTemporelleForm()
    
    return render(request, 'core/creer_capsule.html', {'form': form})


@login_required
def liste_capsules(request):
    """
    List all time capsules (locked and opened)
    """
    capsules = CapsuleTemporelle.objects.filter(
        souvenir__utilisateur=request.user
    )
    
    locked = capsules.filter(is_opened=False).order_by('date_ouverture')
    opened = capsules.filter(is_opened=True).order_by('-date_ouverture_reelle')
    
    # Check for capsules ready to open
    today = timezone.now().date()
    ready_to_open = locked.filter(date_ouverture__lte=today)
    
    context = {
        'locked_capsules': locked,
        'opened_capsules': opened,
        'ready_to_open': ready_to_open,
    }
    
    return render(request, 'core/liste_capsules.html', context)


@login_required
def ouvrir_capsule(request, capsule_id):
    """
    Open a time capsule
    """
    capsule = get_object_or_404(
        CapsuleTemporelle,
        id=capsule_id,
        souvenir__utilisateur=request.user
    )
    
    # Check if already opened
    if capsule.is_opened:
        return render(request, 'core/detail_capsule.html', {'capsule': capsule})
    
    # Check if ready to open
    if capsule.date_ouverture > timezone.now().date():
        messages.warning(request, f'⏰ This capsule opens on {capsule.date_ouverture}')
        return redirect('core:liste_capsules')
    
    # Handle reflection form
    if request.method == 'POST':
        reflexion = request.POST.get('reflexion')
        emotion_reelle = request.POST.get('emotion_reelle')
        
        capsule.is_opened = True
        capsule.date_ouverture_reelle = timezone.now()
        capsule.reflexion_ouverture = reflexion
        capsule.emotion_reelle = emotion_reelle
        capsule.save()
        
        messages.success(request, '🎉 Time capsule opened! Welcome back to this memory.')
        return redirect('core:detail_capsule', capsule_id=capsule.id)
    
    return render(request, 'core/ouvrir_capsule.html', {
        'capsule': capsule,
        'emotion_choices': Souvenir.EMOTION_CHOICES
    })


@login_required
def detail_capsule(request, capsule_id):
    """
    View details of an opened capsule
    """
    capsule = get_object_or_404(
        CapsuleTemporelle,
        id=capsule_id,
        souvenir__utilisateur=request.user
    )
    
    if not capsule.is_opened:
        return redirect('core:ouvrir_capsule', capsule_id=capsule.id)
    
    # Calculate growth metrics
    prediction_correct = capsule.emotion_predite_par_ia == capsule.emotion_reelle
    
    context = {
        'capsule': capsule,
        'prediction_correct': prediction_correct,
    }
    
    return render(request, 'core/detail_capsule.html', context)


# ============================================
# ALBUM VIEWS
# ============================================

@login_required
def liste_albums(request):
    """
    List all memory albums
    """
    albums = AlbumSouvenir.objects.filter(
        utilisateur=request.user
    ).annotate(souvenirs_total=Count('souvenirs'))

    # Get AI suggestions for new albums
    suggestions = AIAnalysisService.generate_album_suggestions(request.user)

    context = {
        'albums': albums,
        'suggestions': suggestions,
    }

    return render(request, 'core/liste_albums.html', context)


@login_required
def creer_album(request):
    """
    Create a new album
    """
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        souvenir_ids = request.POST.getlist('souvenirs')
        
        album = AlbumSouvenir.objects.create(
            utilisateur=request.user,
            titre=titre,
            description=description
        )
        
        if souvenir_ids:
            album.souvenirs.set(souvenir_ids)
        
        messages.success(request, f'📚 Album "{titre}" created successfully!')
        return redirect('core:detail_album', album_id=album.id)
    
    # Get all user memories for selection
    souvenirs = Souvenir.objects.filter(utilisateur=request.user).order_by('-date_evenement')
    
    # Get pre-selected souvenirs from URL parameters
    preselected_ids = request.GET.getlist('souvenirs')
    preselected_title = request.GET.get('title', '')
    preselected_description = request.GET.get('description', '')
    
    context = {
        'souvenirs': souvenirs,
        'preselected_ids': preselected_ids,
        'preselected_title': preselected_title,
        'preselected_description': preselected_description,
    }
    
    return render(request, 'core/creer_album.html', context)


@login_required
def creer_album_depuis_suggestion(request):
    """
    Create a new album from an AI suggestion
    """
    if request.method == 'POST':
        suggestion_type = request.POST.get('suggestion_type')
        theme = request.POST.get('theme')
        year = request.POST.get('year')
        titre = request.POST.get('titre')
        description = request.POST.get('description')

        # Get souvenir IDs based on suggestion parameters
        souvenir_ids = AIAnalysisService.get_souvenir_ids_for_suggestion(
            user=request.user,
            suggestion_type=suggestion_type,
            theme=theme,
            year=year
        )

        # Create the album
        album = AlbumSouvenir.objects.create(
            utilisateur=request.user,
            titre=titre,
            description=description,
            is_auto_generated=True  # Mark as AI-generated
        )

        # Add the souvenirs to the album
        if souvenir_ids:
            album.souvenirs.set(souvenir_ids)

        messages.success(request, f'📚 Album "{titre}" created successfully with {len(souvenir_ids)} memories!')
        return redirect('core:detail_album', album_id=album.id)

    # If not POST, redirect to album list
    return redirect('core:liste_albums')


@login_required
def detail_album(request, album_id):
    """
    View album details
    """
    album = get_object_or_404(AlbumSouvenir, id=album_id, utilisateur=request.user)
    souvenirs = album.souvenirs.all().order_by('-date_evenement')
    
    context = {
        'album': album,
        'souvenirs': souvenirs,
    }
    
    return render(request, 'core/detail_album.html', context)


@login_required
def modifier_album(request, album_id):
    """
    Edit an existing album
    """
    album = get_object_or_404(AlbumSouvenir, id=album_id, utilisateur=request.user)
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        souvenir_ids = request.POST.getlist('souvenirs')
        
        album.titre = titre
        album.description = description
        album.save()
        
        if souvenir_ids:
            album.souvenirs.set(souvenir_ids)
        else:
            album.souvenirs.clear()
        
        messages.success(request, f'📚 Album "{titre}" updated successfully!')
        return redirect('core:detail_album', album_id=album.id)
    
    # Get all user memories for selection
    souvenirs = Souvenir.objects.filter(utilisateur=request.user).order_by('-date_evenement')
    
    context = {
        'album': album,
        'souvenirs': souvenirs,
    }
    
    return render(request, 'core/modifier_album.html', context)


@login_required
def supprimer_album(request, album_id):
    """
    Delete an album
    """
    album = get_object_or_404(AlbumSouvenir, id=album_id, utilisateur=request.user)
    
    if request.method == 'POST':
        titre = album.titre
        album.delete()
        messages.success(request, f'📚 Album "{titre}" deleted successfully!')
        return redirect('core:liste_albums')
    
    context = {
        'album': album,
    }
    
    return render(request, 'core/supprimer_album.html', context)


# ============================================
# PDF EXPORT VIEWS
# ============================================

@login_required
def exporter_pdf(request):
    """
    AJAX endpoint to start PDF export process
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get export parameters from POST data
        titre_export = request.POST.get('titre_export', f'My Memories - {timezone.now().strftime("%Y-%m-%d")}')
        souvenir_ids = request.POST.getlist('souvenirs[]')
        inclure_photos = request.POST.get('inclure_photos', 'true').lower() == 'true'
        style_template = request.POST.get('style_template', 'modern')
        
        if not souvenir_ids:
            return JsonResponse({'error': 'No memories selected for export'}, status=400)
        
        # Get the selected souvenirs
        souvenirs = Souvenir.objects.filter(
            id__in=souvenir_ids,
            utilisateur=request.user
        ).order_by('-date_evenement')
        
        if not souvenirs.exists():
            return JsonResponse({'error': 'No valid memories found'}, status=400)
        
        # Create export record
        export_pdf = ExportPDF.objects.create(
            utilisateur=request.user,
            titre_export=titre_export,
            inclure_photos=inclure_photos,
            style_template=style_template,
            status='processing'
        )
        
        # Add souvenirs to export
        export_pdf.souvenirs.set(souvenirs)
        
        # Generate PDF asynchronously (for now, do it synchronously)
        try:
            pdf_buffer = generate_pdf_content(export_pdf)
            
            # Save PDF file
            filename = f"memories_export_{export_pdf.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            export_pdf.fichier_pdf.save(filename, pdf_buffer)
            export_pdf.status = 'ready'
            export_pdf.nombre_pages = 1  # We'll calculate this properly later
            export_pdf.save()
            
            return JsonResponse({
                'success': True,
                'export_id': export_pdf.id,
                'download_url': reverse('core:telecharger_pdf', args=[export_pdf.id]),
                'message': f'PDF export "{titre_export}" created successfully!'
            })
            
        except Exception as e:
            export_pdf.status = 'error'
            export_pdf.save()
            logger.error(f'PDF generation failed for export {export_pdf.id}: {str(e)}')
            return JsonResponse({'error': f'PDF generation failed: {str(e)}'}, status=500)
    
    except Exception as e:
        logger.error(f'PDF export creation failed: {str(e)}')
        return JsonResponse({'error': 'Failed to create PDF export'}, status=500)


@login_required
def telecharger_pdf(request, export_id):
    """
    Download a completed PDF export
    """
    export_pdf = get_object_or_404(
        ExportPDF,
        id=export_id,
        utilisateur=request.user,
        status='ready'
    )
    
    if not export_pdf.fichier_pdf:
        messages.error(request, 'PDF file not found')
        return redirect('core:memories_dashboard')
    
    # Return PDF file
    response = HttpResponse(export_pdf.fichier_pdf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{export_pdf.titre_export}.pdf"'
    return response


@login_required
def liste_exports_pdf(request):
    """
    List user's PDF exports
    """
    exports = ExportPDF.objects.filter(utilisateur=request.user).order_by('-date_export')
    return render(request, 'core/liste_exports_pdf.html', {'exports': exports})


def generate_pdf_content(export_pdf):
    """
    Generate PDF content using xhtml2pdf
    """
    from xhtml2pdf import pisa
    from io import BytesIO
    
    # Get souvenirs with related data
    souvenirs = export_pdf.souvenirs.all().prefetch_related('analyse_ia').order_by('-date_evenement')
    
    # Prepare context for template
    context = {
        'export': export_pdf,
        'souvenirs': souvenirs,
        'user': export_pdf.utilisateur,
        'generated_at': timezone.now(),
    }
    
    # Render HTML template
    html_content = render_to_string('core/pdf_export_template.html', context)
    
    # Create PDF
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    
    if pisa_status.err:
        raise Exception('PDF generation failed')
    
    pdf_buffer.seek(0)
    return pdf_buffer