
from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.db import models
from .models import User, Souvenir, CapsuleTemporelle, EntreeJournal, Tag, Humeur
from django.core.exceptions import ValidationError
import os


class UserCreationForm(BaseUserCreationForm):
    """Custom user creation form for core.User model"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email address'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm Password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class SouvenirForm(forms.ModelForm):
    """Secure form for adding/editing memories with AI features"""
    
    emotion = forms.ChoiceField(
        choices=Souvenir.EMOTION_CHOICES,
        required=False,
        initial='neutral',
        widget=forms.Select(attrs={'class': 'form-input'}),
        label='Primary Emotion',
        help_text='Select the main emotion you felt'
    )
    
    theme = forms.ChoiceField(
        choices=Souvenir.THEME_CHOICES,
        required=False,
        initial='other',
        widget=forms.Select(attrs={'class': 'form-input'}),
        label='Theme',
        help_text='Categorize this memory'
    )
    
    class Meta:
        model = Souvenir
        fields = [
            'titre', 'description', 'date_evenement',
            'photo', 'video',
            'emotion', 'theme', 'lieu', 'personnes_presentes',
            'is_favorite'
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Memory title',
                'maxlength': 200,
                'required': False
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Describe your memory...',
                'rows': 8,
                'required': False
            }),
            'date_evenement': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': False
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/jpeg,image/png,image/jpg,image/gif,image/webp'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'video/mp4,video/avi,video/mov,video/wmv'
            }),
            'lieu': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Paris, France'
            }),
            'personnes_presentes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Marie, Paul, Sophie (comma-separated)',
                'rows': 3
            }),
            'is_favorite': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }
        labels = {
            'titre': 'Title',
            'description': 'Description',
            'date_evenement': 'Event Date',
            'photo': 'Photo (optional)',
            'video': 'Video (optional)',
            'lieu': 'Location',
            'personnes_presentes': 'People Present',
            'is_favorite': 'Mark as favorite'
        }
        help_texts = {
            'lieu': 'Where did this happen?',
            'personnes_presentes': 'Who was there with you?'
        }
    
    def clean_titre(self):
        """Title validation"""
        titre = self.cleaned_data.get('titre')
        if not titre or titre.strip() == '':
            raise ValidationError('Title cannot be empty.')
        if len(titre) < 3:
            raise ValidationError('Title must be at least 3 characters long.')
        return titre.strip()
    
    def clean_description(self):
        """Description validation"""
        description = self.cleaned_data.get('description')
        if not description or description.strip() == '':
            raise ValidationError('Description cannot be empty.')
        if len(description) < 10:
            raise ValidationError('Description must be at least 10 characters long.')
        return description.strip()
    
    def clean_photo(self):
        """Photo validation"""
        photo = self.cleaned_data.get('photo')
        if photo:
            # Check extension
            ext = os.path.splitext(photo.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if ext not in valid_extensions:
                raise ValidationError(f'Invalid file format. Use: {", ".join(valid_extensions)}')
            
            # Check size (10 MB max)
            if photo.size > 10 * 1024 * 1024:
                raise ValidationError('Photo must not exceed 10 MB.')
        
        return photo
    
    def clean_video(self):
        """Video validation"""
        video = self.cleaned_data.get('video')
        if video:
            # Check extension
            ext = os.path.splitext(video.name)[1].lower()
            valid_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.mkv']
            if ext not in valid_extensions:
                raise ValidationError(f'Invalid file format. Use: {", ".join(valid_extensions)}')
            
            # Check size (100 MB max)
            if video.size > 100 * 1024 * 1024:
                raise ValidationError('Video must not exceed 100 MB.')
        
        return video


class CapsuleTemporelleForm(forms.ModelForm):
    """Form for creating time capsules"""
    
    class Meta:
        model = Souvenir
        fields = ['titre', 'description', 'date_evenement', 'photo', 'video']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Time capsule title',
                'required': False
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'What do you want to remember?',
                'rows': 8,
                'required': False
            }),
            'date_evenement': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
                'required': False
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-input',
                'required': False
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-input',
                'required': False
            }),
        }
    
    message_futur = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Write a message to your future self...',
            'rows': 6
        }),
        label='Message to Future Self',
        help_text='This will be shown when the capsule opens. Leave empty for AI-generated message.',
        required=False
    )
    
    date_ouverture = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date',
            'required': False
        }),
        label='Opening Date',
        help_text='When should this capsule unlock?',
        required=False
    )


class UserProfileForm(forms.ModelForm):
    """Form for user profile management"""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email address'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last name'
            }),
        }
        labels = {
            'username': 'Username',
            'email': 'Email Address',
            'first_name': 'First Name',
            'last_name': 'Last Name'
        }

    def clean_username(self):
        """Validate username uniqueness"""
        username = self.cleaned_data.get('username')
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError('This email address is already in use.')
        return email
class EntreeJournalForm(forms.ModelForm):
    """Form for creating/editing a journal entry"""
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.none(),  # Will be set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox-list'}),
        label='Tags',
        help_text='Select tags to categorize this entry'
    )
    
    humeurs = forms.ModelMultipleChoiceField(
        queryset=Humeur.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox-list'}),
        label='Moods',
        help_text='Select your current moods'
    )
    
    class Meta:
        model = EntreeJournal
        fields = ['titre', 'contenu_texte', 'lieu', 'meteo', 'is_favorite', 'is_public']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Entry title',
                'maxlength': 200,
                'id': 'id_titre'
            }),
            'contenu_texte': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Write your journal here...',
                'rows': 10,
                'id': 'id_contenu_texte'
            }),
            'lieu': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Where are you? (optional)'
            }),
            'meteo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'What is the weather like? (optional)'
            }),
            'is_favorite': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }
        labels = {
            'titre': 'Title',
            'contenu_texte': 'Content',
            'lieu': 'Location',
            'meteo': 'Weather',
            'is_favorite': 'Mark as favorite',
            'is_public': 'Make public'
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter tags by user (user's tags + global tags)
        if user:
            self.fields['tags'].queryset = Tag.objects.filter(
                models.Q(utilisateur=user) | models.Q(utilisateur__isnull=True)
            )
        else:
            self.fields['tags'].queryset = Tag.objects.filter(utilisateur__isnull=True)
        
        # If editing, pre-select existing tags and humeurs
        if self.instance.pk:
            self.fields['tags'].initial = [et.tag for et in self.instance.entree_tags.all()]
            self.fields['humeurs'].initial = [eh.humeur for eh in self.instance.entree_humeurs.all()]
    
    def clean_titre(self):
        """Title validation"""
        titre = self.cleaned_data.get('titre')
        if not titre or titre.strip() == '':
            raise ValidationError('Title cannot be empty.')
        if len(titre) < 3:
            raise ValidationError('Title must be at least 3 characters long.')
        return titre.strip()
    
    def clean_contenu_texte(self):
        """Content validation"""
        contenu = self.cleaned_data.get('contenu_texte')
        if not contenu or contenu.strip() == '':
            raise ValidationError('Content cannot be empty.')
        if len(contenu) < 10:
            raise ValidationError('Content must be at least 10 characters long.')
        return contenu.strip()


class TagForm(forms.ModelForm):
    """Form for creating/editing a tag"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Tag
        fields = ['nom', 'couleur', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Tag name',
                'maxlength': 50
            }),
            'couleur': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color',
                'value': '#3498db'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Description (optional)',
                'rows': 3
            })
        }
        labels = {
            'nom': 'Tag name',
            'couleur': 'Color',
            'description': 'Description'
        }
    
    def clean_nom(self):
        """Name validation"""
        nom = self.cleaned_data.get('nom')
        if not nom or nom.strip() == '':
            raise ValidationError('Name cannot be empty.')
        if len(nom) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        
        # Check for duplicate tag name for the current user
        if self.user:
            # Exclude current instance when editing
            queryset = Tag.objects.filter(nom=nom.strip(), utilisateur=self.user)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError(f'You already have a tag with the name "{nom.strip()}".')
        
        return nom.strip()


class HumeurForm(forms.ModelForm):
    """Form for creating/editing a mood (admin only)"""
    
    class Meta:
        model = Humeur
        fields = ['nom', 'emoji', 'couleur', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Mood name',
                'maxlength': 50
            }),
            'emoji': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '😊',
                'maxlength': 10
            }),
            'couleur': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color',
                'value': '#FFD700'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Description (optional)',
                'rows': 3
            })
        }
        labels = {
            'nom': 'Mood name',
            'emoji': 'Emoji',
            'couleur': 'Color',
            'description': 'Description'
        }


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar_url']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email'
            }),
            'avatar_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'Avatar URL (optional)'
            })
        }
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email',
            'avatar_url': 'Avatar URL'
        }
