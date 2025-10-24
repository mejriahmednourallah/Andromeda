from django.shortcuts import render, get_object_or_404, redirect
from .models import Note, User
from .forms import UserCreationForm
from django.contrib.auth import login

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
            return redirect('core:index')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})