from django.shortcuts import render, get_object_or_404, redirect
from .models import Note, User, Souvenir
from .forms import UserCreationForm, SouvenirForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import logging, os, json, requests

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
                
                # Message de succès
                messages.success(request, f'Souvenir "{souvenir.titre}" ajouté avec succès!')
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
            # Afficher les erreurs du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
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
    Vue pour supprimer un souvenir.
    Vérifie que l'utilisateur est bien le propriétaire.
    """
    souvenir = get_object_or_404(Souvenir, id=souvenir_id, utilisateur=request.user)
    
    if request.method == 'POST':
        titre = souvenir.titre
        souvenir.delete()
        messages.success(request, f'Souvenir "{titre}" supprimé avec succès.')
        logger.info(f'Souvenir {souvenir_id} supprimé par {request.user.username}')
        return redirect('core:liste_souvenirs')
    
    return render(request, 'core/supprimer_souvenir.html', {'souvenir': souvenir})


@login_required
def moodai(request):
    """
    Page MoodAI: interface d'analyse émotionnelle côté client.
    """
    return render(request, 'core/moodai.html')


def _local_emotion_scores(text: str):
    """Heuristique locale de repli pour fournir un score par catégorie."""
    t = (text or '').lower()
    tokens = [w for w in ''.join([c if c.isalpha() or c.isspace() else ' ' for c in t]).split() if w]
    lex = {
        'positif': {'super','bien','genial','excellent','parfait','heureux','cool','merci','bravo','fantastique','content','love','aime','satisfait','enthousiaste'},
        'negatif': {'mauvais','horrible','nul','decu','decevant','pire','fatigue','mal','probleme','erreur','bug','rate','peur','anxieux'},
        'colere': {'colere','furieux','fache','rage','enervant','frustre','agace','mechant','inacceptable','critique','attaque','haine'},
        'tristesse': {'triste','deprime','chagrin','pleurer','solitaire','perdu','morose','melancolie','tristesse'},
    }
    scores = { 'positif': 0.0, 'neutre': 0.0001, 'negatif': 0.0, 'colere': 0.0, 'tristesse': 0.0 }
    if not tokens:
        scores['neutre'] = 1.0
        return scores
    for w in tokens:
        for k in ('positif','negatif','colere','tristesse'):
            if w in lex[k]:
                scores[k] += 1.0
    if scores['positif']==0 and (scores['negatif']+scores['colere']+scores['tristesse'])==0:
        scores['neutre'] = 1.0
    return scores


@csrf_exempt
@login_required
@require_POST
def moodai_analyze(request):
    """
    Endpoint JSON: { text: "..." }
    Appelle Hugging Face Inference API (modèle par défaut multilingue 3 classes) et
    renvoie des scores normalisés sur nos catégories: positif, neutre, negatif, colere, tristesse.
    Si la clé ou l'appel échoue, bascule sur l'heuristique locale.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
        text = payload.get('text', '')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    hf_key = os.environ.get('HF_API_KEY') or os.environ.get('HUGGINGFACE_API_KEY')
    model = os.environ.get('HF_MODEL', 'cardiffnlp/twitter-xlm-roberta-base-sentiment')

    def normalize_sentiment(scores3):
        # scores3: list of dicts with label and score
        out = { 'positif': 0.0, 'neutre': 0.0, 'negatif': 0.0, 'colere': 0.0, 'tristesse': 0.0 }
        for it in scores3:
            lab = it.get('label','').lower()
            if 'pos' in lab:
                out['positif'] = it.get('score',0.0)
            elif 'neu' in lab:
                out['neutre'] = it.get('score',0.0)
            elif 'neg' in lab:
                # Répartir une partie vers colère/tristesse en restant simple
                neg = it.get('score',0.0)
                out['negatif'] = max(0.0, neg - 0.0001)
            
        # Petite redistribution négative basée sur mots-clés
        local = _local_emotion_scores(text)
        neg_family = local['negatif'] + local['colere'] + local['tristesse']
        if neg_family > 0 and (out['negatif']>0 or out['neutre']>0 or out['positif']>0):
            total_local_neg = neg_family
            out['colere'] = out['negatif'] * (local['colere']/total_local_neg)
            out['tristesse'] = out['negatif'] * (local['tristesse']/total_local_neg)
            out['negatif'] = out['negatif'] * (local['negatif']/total_local_neg)
        return out

    if not hf_key:
        scores = _local_emotion_scores(text)
        top = max(scores, key=scores.get)
        return JsonResponse({ 'source': 'local', 'top': top, 'scores': scores })

    try:
        resp = requests.post(
            f'https://api-inference.huggingface.co/models/{model}',
            headers={'Authorization': f'Bearer {hf_key}', 'Content-Type': 'application/json'},
            json={ 'inputs': text },
            timeout=20
        )
        if resp.status_code == 503:
            # Le modèle est en chargement; bascule local
            scores = _local_emotion_scores(text)
            top = max(scores, key=scores.get)
            return JsonResponse({ 'source': 'local', 'top': top, 'scores': scores, 'detail': 'model_loading' }, status=200)
        resp.raise_for_status()
        data = resp.json()
        # data est généralement [[{label, score}...]]
        flat = data[0] if isinstance(data, list) and data and isinstance(data[0], list) else data
        scores = normalize_sentiment(flat)
        top = max(scores, key=scores.get)
        return JsonResponse({ 'source': 'huggingface', 'model': model, 'top': top, 'scores': scores })
    except Exception as e:
        scores = _local_emotion_scores(text)
        top = max(scores, key=scores.get)
        return JsonResponse({ 'source': 'local', 'top': top, 'scores': scores, 'error': str(e) }, status=200)