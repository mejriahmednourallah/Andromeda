from django.shortcuts import render, get_object_or_404, redirect
from .models import Note, User
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Create a few sample notes for demo if DB empty
def ensure_sample_notes():
    if Note.objects.count() == 0:
        # create a default user if none
        user = None
        if User.objects.exists():
            user = User.objects.first()
        else:
            user = User.objects.create_user(username='demo', password='demo')
            user.first_name = 'Bruce'
            user.last_name = 'Wayne'
            user.save()

        samples = [
            ('The Great Gatsby', 'A classic novel card — demo content.'),
            ('One Hundred Years of Solitude', 'Magical realist note star.'),
            ('To Kill a Mockingbird', 'A note about justice and growth.'),
            ('Of Human Bondage', 'Classic literature sample.'),
            ('Breaking Dawn', 'Popular fiction example.'),
        ]
        for t, b in samples:
            Note.objects.create(owner=user, title=t, body=b)

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