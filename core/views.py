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
    CapsuleTemporelle, PartageSouvenir, SuiviMotivationnel, ExportPDF , HistoireInspirante
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
# EMOTIONAL CALENDAR VIEW
# ============================================

@login_required
def calendrier_emotionnel(request):
    """
    Display emotional timeline view organized by year and date
    """
    # Get user's memories
    souvenirs = Souvenir.objects.filter(utilisateur=request.user).order_by('-date_evenement')
    
    # Emotion color mapping
    emotion_colors = {
        'joy': '#FFD700',        # Gold
        'sadness': '#4169E1',    # Royal Blue
        'nostalgia': '#9370DB',  # Medium Purple
        'gratitude': '#32CD32',  # Lime Green
        'excitement': '#FF4500', # Orange Red
        'peace': '#98FB98',      # Pale Green
        'love': '#FF69B4',       # Hot Pink
        'surprise': '#FFA500',   # Orange
        'pride': '#DC143C',      # Crimson
        'neutral': '#808080',    # Gray
    }
    
    # Organize memories by year and month
    memories_by_year = {}
    
    for souvenir in souvenirs:
        year = souvenir.date_evenement.year
        month = souvenir.date_evenement.strftime('%Y-%m')  # YYYY-MM format for sorting
        
        if year not in memories_by_year:
            memories_by_year[year] = {}
        
        if month not in memories_by_year[year]:
            memories_by_year[year][month] = []
        
        # Add emotion color to each memory
        souvenir.emotion_color = emotion_colors.get(souvenir.emotion, '#808080')
        memories_by_year[year][month].append(souvenir)
    
    # Sort months within each year
    for year in memories_by_year:
        memories_by_year[year] = dict(sorted(memories_by_year[year].items()))
    
    # Sort years in descending order
    memories_by_year = dict(sorted(memories_by_year.items(), reverse=True))
    
    context = {
        'memories_by_year': memories_by_year,
        'emotion_colors': emotion_colors,
        'total_memories': souvenirs.count(),
    }
    
    return render(request, 'core/calendrier_emotionnel.html', context)


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


@login_required
def story_inspiration(request):
    """
    Vue pour la page Story - génération d'histoires inspirantes
    """
    story_data = None
    reflexion_text = ""
    histoire_saved = None
    
    if request.method == 'POST':
        reflexion_text = request.POST.get('reflexion_text', '').strip()
        
        if reflexion_text:
            try:
                # Générer l'histoire inspirante avec l'IA
                story_data = AIRecommendationService.generate_inspirational_story(reflexion_text)
                
                # Sauvegarder l'histoire dans la base de données
                histoire_saved = HistoireInspirante.objects.create(
                    utilisateur=request.user,
                    reflexion_text=reflexion_text,
                    histoire_generee=story_data['story'],
                    celebrite=story_data['celebrity'],
                    est_simulee=story_data.get('simulated', True),
                    modele_utilise=story_data.get('model', '')
                )
                
                logger.info(f"Histoire inspirante sauvegardée (ID: {histoire_saved.id}) pour l'utilisateur {request.user.username}")
                messages.success(request, "✨ Votre histoire inspirante a été générée et sauvegardée !")
                
            except Exception as e:
                logger.error(f"Error generating story: {str(e)}")
                messages.error(request, "Une erreur s'est produite lors de la génération de l'histoire. Veuillez réessayer.")
        else:
            messages.warning(request, "Veuillez entrer une réflexion pour générer une histoire inspirante.")
    
    context = {
        'story_data': story_data,
        'reflexion_text': reflexion_text,
        'histoire_saved': histoire_saved,
    }
    
    return render(request, 'core/story_inspiration.html', context)


@login_required
def story_history(request):
    """
    Vue pour afficher l'historique de toutes les histoires inspirantes de l'utilisateur
    """
    # Récupérer toutes les histoires de l'utilisateur
    histoires = HistoireInspirante.objects.filter(utilisateur=request.user).order_by('-created_at')
    
    # Filtres
    filter_favorite = request.GET.get('favorite', None)
    filter_simulated = request.GET.get('simulated', None)
    search_query = request.GET.get('search', '')
    
    if filter_favorite == 'true':
        histoires = histoires.filter(is_favorite=True)
    
    if filter_simulated == 'true':
        histoires = histoires.filter(est_simulee=True)
    elif filter_simulated == 'false':
        histoires = histoires.filter(est_simulee=False)
    
    if search_query:
        histoires = histoires.filter(
            Q(celebrite__icontains=search_query) | 
            Q(reflexion_text__icontains=search_query) |
            Q(histoire_generee__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(histoires, 10)  # 10 histoires par page
    page_number = request.GET.get('page')
    histoires_page = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': HistoireInspirante.objects.filter(utilisateur=request.user).count(),
        'favorites': HistoireInspirante.objects.filter(utilisateur=request.user, is_favorite=True).count(),
        'simulated': HistoireInspirante.objects.filter(utilisateur=request.user, est_simulee=True).count(),
        'ai_generated': HistoireInspirante.objects.filter(utilisateur=request.user, est_simulee=False).count(),
    }
    
    context = {
        'histoires': histoires_page,
        'stats': stats,
        'filter_favorite': filter_favorite,
        'filter_simulated': filter_simulated,
        'search_query': search_query,
    }
    
    return render(request, 'core/story_history.html', context)


@login_required
def toggle_histoire_favorite(request, histoire_id):
    """
    Toggle favorite status for a story
    """
    histoire = get_object_or_404(HistoireInspirante, id=histoire_id, utilisateur=request.user)
    histoire.is_favorite = not histoire.is_favorite
    histoire.save()
    
    status = "ajoutée aux" if histoire.is_favorite else "retirée des"
    messages.success(request, f'✨ Histoire {status} favorites!')
    
    # Redirect back to history or story page
    return redirect(request.META.get('HTTP_REFERER', 'core:story_history'))


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


@login_required
def calendrier_emotionnel(request):
    """
    Display emotional calendar with yearly overview and monthly detail views
    """
    # Get user's memories
    souvenirs = Souvenir.objects.filter(utilisateur=request.user)
    
    # Get selected year from URL parameter, default to current year
    selected_year = request.GET.get('year')
    if selected_year:
        try:
            selected_year = int(selected_year)
            # Validate year is within reasonable bounds
            if selected_year < 2000 or selected_year > 2030:
                selected_year = timezone.now().year
        except ValueError:
            selected_year = timezone.now().year
    else:
        selected_year = timezone.now().year
    
    # Get all available years for navigation
    available_years = souvenirs.values_list('date_evenement__year', flat=True).distinct().order_by('-date_evenement__year')
    available_years = list(available_years)
    
    # Emotion color mapping with pastel tones
    emotion_colors = {
        'joy': '#FEF3C7',        # Soft yellow
        'sadness': '#DBEAFE',    # Soft blue
        'nostalgia': '#E9D5FF',  # Soft purple
        'gratitude': '#D1FAE5',  # Soft green
        'excitement': '#FED7AA', # Soft orange
        'peace': '#F0FDF4',      # Very soft green
        'love': '#FCE7F3',       # Soft pink
        'surprise': '#FEF3C7',   # Soft yellow
        'pride': '#FEE2E2',      # Soft red
        'anger': '#FEE2E2',      # Soft red
        'stress': '#FEF3C7',     # Soft yellow
        'calm': '#F0FDF4',       # Very soft green
        'neutral': '#F9FAFB',    # Light gray
    }
    yearly_data = []
    
    for month in range(12):
        month_data = {
            'month': month,
            'year': selected_year,
            'month_name': ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December'][month],
            'days': [],
            'memory_count': 0,
            'dominant_emotion': 'No data',
            'dominant_color': '#f3f4f6'
        }
        
        # Get memories for this month
        month_memories = souvenirs.filter(
            date_evenement__year=selected_year,
            date_evenement__month=month + 1
        )
        
        month_data['memory_count'] = month_memories.count()
        
        # Calculate emotion distribution for the month
        emotion_counts = {}
        for memory in month_memories:
            emotion = memory.ai_emotion_detected if memory.ai_emotion_detected else memory.emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        if emotion_counts:
            dominant_emotion = max(emotion_counts.keys(), key=lambda x: emotion_counts[x])
            month_data['dominant_emotion'] = dominant_emotion.title()
            month_data['dominant_color'] = emotion_colors.get(dominant_emotion, '#f3f4f6')
        
        # Generate mini calendar days
        import calendar
        from datetime import date
        
        cal = calendar.monthcalendar(selected_year, month + 1)
        day_emotions = {}
        
        # Map memories to days
        for memory in month_memories:
            day = memory.date_evenement.day
            emotion = memory.ai_emotion_detected if memory.ai_emotion_detected else memory.emotion
            if day not in day_emotions:
                day_emotions[day] = []
            day_emotions[day].append(emotion)
        
        # Create day data for mini calendar
        for week in cal:
            for day_num in week:
                if day_num == 0:
                    # Empty day from previous/next month
                    month_data['days'].append({
                        'class': 'empty',
                        'color': '#f9fafb',
                        'date': '',
                        'emotion': None
                    })
                else:
                    emotions = day_emotions.get(day_num, [])
                    if emotions:
                        # Use the most common emotion for the day
                        emotion_counts = {}
                        for emotion in emotions:
                            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                        dominant_day_emotion = max(emotion_counts.keys(), key=lambda x: emotion_counts[x])
                        color = emotion_colors.get(dominant_day_emotion, '#f9fafb')
                        day_class = 'has-memory'
                    else:
                        color = '#f9fafb'
                        day_class = 'empty'
                        dominant_day_emotion = None
                    
                    month_data['days'].append({
                        'class': day_class,
                        'color': color,
                        'date': f"{selected_year}-{month+1:02d}-{day_num:02d}",
                        'emotion': dominant_day_emotion
                    })
        
        yearly_data.append(month_data)
    
    context = {
        'emotion_colors': emotion_colors,
        'yearly_data': yearly_data,
        'selected_year': selected_year,
        'available_years': available_years,
        'current_year': timezone.now().year,
    }
    
    return render(request, 'core/calendrier_emotionnel.html', context)


@login_required
def calendrier_emotionnel_events(request):
    """
    Return JSON events for FullCalendar
    """
    # Emotion color mapping - therapeutic pastel colors
    emotion_colors = {
        'joy': '#FEF3C7',        # Soft yellow
        'sadness': '#DBEAFE',    # Soft blue
        'nostalgia': '#E9D5FF',  # Soft purple
        'gratitude': '#D1FAE5',  # Soft green
        'excitement': '#FED7AA', # Soft orange
        'peace': '#F0FDF4',      # Very soft green
        'love': '#FCE7F3',       # Soft pink
        'surprise': '#FEF3C7',   # Soft yellow
        'pride': '#FEE2E2',      # Soft red
        'anger': '#FEE2E2',      # Soft red
        'stress': '#FEF3C7',     # Soft yellow
        'calm': '#F0FDF4',       # Very soft green
        'neutral': '#F9FAFB',    # Soft gray
    }
    
    # Get user's memories
    souvenirs = Souvenir.objects.filter(utilisateur=request.user)
    
    events = []
    for souvenir in souvenirs:
        # Use AI-detected emotion if available, otherwise use user emotion
        emotion = souvenir.ai_emotion_detected if souvenir.ai_emotion_detected else souvenir.emotion
        color = emotion_colors.get(emotion, '#808080')  # Default to gray
        
        events.append({
            'title': f"{souvenir.titre} ({emotion})",
            'start': souvenir.date_evenement.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'textColor': '#000000',
            'url': reverse('core:detail_souvenir', kwargs={'souvenir_id': souvenir.id}),
            'extendedProps': {
                'emotion': emotion,
                'description': souvenir.description[:100] + '...' if len(souvenir.description) > 100 else souvenir.description,
                'has_media': souvenir.has_media,
            }
        })
    
    return JsonResponse(events, safe=False)


@login_required
def calendrier_emotionnel_day_memories(request):
    """
    Return JSON data for memories on a specific day
    """
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date parameter required'}, status=400)
    
    try:
        from datetime import datetime
        date = datetime.fromisoformat(date_str).date()
        
        # Get memories for this specific day
        memories = Souvenir.objects.filter(
            utilisateur=request.user,
            date_evenement__date=date
        ).order_by('-date_evenement')
        
        # Emotion color mapping
        emotion_colors = {
            'joy': '#FEF3C7',
            'sadness': '#DBEAFE',
            'nostalgia': '#E9D5FF',
            'gratitude': '#D1FAE5',
            'excitement': '#FED7AA',
            'peace': '#F0FDF4',
            'love': '#FCE7F3',
            'surprise': '#FEF3C7',
            'pride': '#FEE2E2',
            'anger': '#FEE2E2',
            'stress': '#FEF3C7',
            'calm': '#F0FDF4',
            'neutral': '#F9FAFB',
        }
        
        memories_data = []
        for memory in memories:
            emotion = memory.ai_emotion_detected if memory.ai_emotion_detected else memory.emotion
            memories_data.append({
                'id': memory.id,
                'titre': memory.titre,
                'description': memory.description,
                'date_evenement': memory.date_evenement.isoformat(),
                'emotion': emotion,
                'emotion_display': memory.get_emotion_display(),
                'photo': memory.photo.url if memory.photo else None,
                'video': memory.video.url if memory.video else None,
            })
        
        return JsonResponse({
            'memories': memories_data,
            'date': date_str,
            'count': len(memories_data)
        })
        
    except Exception as e:
        logger.error(f'Error fetching day memories: {str(e)}')
        return JsonResponse({'error': 'Failed to fetch memories'}, status=500)


@login_required
def calendrier_emotionnel_monthly_analytics(request):
    """
    Return JSON data for monthly analytics (emotion distribution, stats)
    """
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not month or not year:
        return JsonResponse({'error': 'Month and year parameters required'}, status=400)
    
    try:
        month = int(month)
        year = int(year)
        
        # Get memories for this month
        month_memories = Souvenir.objects.filter(
            utilisateur=request.user,
            date_evenement__year=year,
            date_evenement__month=month
        )
        
        # Calculate emotion distribution
        emotion_distribution = {}
        theme_distribution = {}
        daily_activity = {}
        
        for memory in month_memories:
            emotion = memory.ai_emotion_detected if memory.ai_emotion_detected else memory.emotion
            emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
            
            # Track themes if available
            if memory.theme:
                theme_distribution[memory.theme] = theme_distribution.get(memory.theme, 0) + 1
            
            # Track daily activity
            day = memory.date_evenement.day
            daily_activity[day] = daily_activity.get(day, 0) + 1
        
        # Calculate stats
        total_memories = month_memories.count()
        days_with_memories = len(daily_activity)
        
        # Calculate month length for activity metrics
        import calendar
        month_length = calendar.monthrange(year, month)[1]
        
        # Memory frequency (memories per active day)
        memory_frequency = total_memories / days_with_memories if days_with_memories > 0 else 0
        
        # Most active day
        most_active_day = max(daily_activity.keys(), key=lambda x: daily_activity[x]) if daily_activity else None
        
        # Emotion diversity (number of different emotions used)
        emotion_diversity = len(emotion_distribution)
        
        # Dominant emotion
        dominant_emotion = 'No data'
        dominant_emotion_count = 0
        if emotion_distribution:
            dominant_emotion = max(emotion_distribution.keys(), key=lambda x: emotion_distribution[x])
            dominant_emotion_count = emotion_distribution[dominant_emotion]
            dominant_emotion = dominant_emotion.title()
        
        # Dominant theme
        dominant_theme = 'No data'
        if theme_distribution:
            dominant_theme = max(theme_distribution.keys(), key=lambda x: theme_distribution[x])
            dominant_theme = dominant_theme.title()
        
        # Calculate activity level
        activity_percentage = (days_with_memories / month_length) * 100
        
        # Get previous month data for comparison
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        
        prev_month_memories = Souvenir.objects.filter(
            utilisateur=request.user,
            date_evenement__year=prev_year,
            date_evenement__month=prev_month
        )
        prev_month_count = prev_month_memories.count()
        
        # Calculate change from previous month
        change_from_prev = total_memories - prev_month_count
        change_percentage = ((total_memories - prev_month_count) / prev_month_count * 100) if prev_month_count > 0 else 0
        
        stats = {
            'total_memories': total_memories,
            'days_with_memories': days_with_memories,
            'dominant_emotion': dominant_emotion,
            'dominant_emotion_count': dominant_emotion_count,
            'dominant_theme': dominant_theme,
            'memory_frequency': round(memory_frequency, 1),
            'most_active_day': most_active_day,
            'emotion_diversity': emotion_diversity,
            'activity_percentage': round(activity_percentage, 1),
            'change_from_prev': change_from_prev,
            'change_percentage': round(change_percentage, 1),
            'month_length': month_length,
        }
        
        return JsonResponse({
            'emotion_distribution': emotion_distribution,
            'theme_distribution': theme_distribution,
            'daily_activity': daily_activity,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f'Error fetching monthly analytics: {str(e)}')
        return JsonResponse({'error': 'Failed to fetch analytics'}, status=500)


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