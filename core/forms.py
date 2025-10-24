
from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User, Souvenir, CapsuleTemporelle
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
            'is_favorite', 'is_public'
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Memory title',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Describe your memory...',
                'rows': 5
            }),
            'date_evenement': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
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
            'personnes_presentes': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Marie, Paul, Sophie (comma-separated)'
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
            'description': 'Description',
            'date_evenement': 'Event Date',
            'photo': 'Photo (optional)',
            'video': 'Video (optional)',
            'lieu': 'Location',
            'personnes_presentes': 'People Present',
            'is_favorite': 'Mark as favorite',
            'is_public': 'Make public'
        }
        help_texts = {
            'lieu': 'Where did this happen?',
            'personnes_presentes': 'Who was there with you?',
            'is_public': 'Public memories can be seen by others'
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
                'placeholder': 'Time capsule title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'What do you want to remember?',
                'rows': 5
            }),
            'date_evenement': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-input'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-input'
            }),
        }
    
    message_futur = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Write a message to your future self...',
            'rows': 4
        }),
        label='Message to Future Self',
        help_text='This will be shown when the capsule opens. Leave empty for AI-generated message.',
        required=False
    )
    
    date_ouverture = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        }),
        label='Opening Date',
        help_text='When should this capsule unlock?'
    )
