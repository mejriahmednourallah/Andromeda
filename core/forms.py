from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User, Souvenir
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
    """Formulaire sécurisé pour l'ajout de souvenirs"""
    
    class Meta:
        model = Souvenir
        fields = ['titre', 'description', 'date_evenement', 'photo', 'video']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Titre du souvenir',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Décrivez votre souvenir...',
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
            })
        }
        labels = {
            'titre': 'Titre',
            'description': 'Description',
            'date_evenement': 'Date de l\'événement',
            'photo': 'Photo (optionnelle)',
            'video': 'Vidéo (optionnelle)'
        }
    
    def clean_titre(self):
        """Validation du titre"""
        titre = self.cleaned_data.get('titre')
        if not titre or titre.strip() == '':
            raise ValidationError('Le titre ne peut pas être vide.')
        if len(titre) < 3:
            raise ValidationError('Le titre doit contenir au moins 3 caractères.')
        return titre.strip()
    
    def clean_description(self):
        """Validation de la description"""
        description = self.cleaned_data.get('description')
        if not description or description.strip() == '':
            raise ValidationError('La description ne peut pas être vide.')
        if len(description) < 10:
            raise ValidationError('La description doit contenir au moins 10 caractères.')
        return description.strip()
    
    def clean_photo(self):
        """Validation de la photo"""
        photo = self.cleaned_data.get('photo')
        if photo:
            # Vérifier l'extension
            ext = os.path.splitext(photo.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if ext not in valid_extensions:
                raise ValidationError(f'Format de fichier non autorisé. Utilisez: {", ".join(valid_extensions)}')
            
            # Vérifier la taille (10 MB max)
            if photo.size > 10 * 1024 * 1024:
                raise ValidationError('La photo ne doit pas dépasser 10 MB.')
        
        return photo
    
    def clean_video(self):
        """Validation de la vidéo"""
        video = self.cleaned_data.get('video')
        if video:
            # Vérifier l'extension
            ext = os.path.splitext(video.name)[1].lower()
            valid_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.mkv']
            if ext not in valid_extensions:
                raise ValidationError(f'Format de fichier non autorisé. Utilisez: {", ".join(valid_extensions)}')
            
            # Vérifier la taille (100 MB max)
            if video.size > 100 * 1024 * 1024:
                raise ValidationError('La vidéo ne doit pas dépasser 100 MB.')
        
        return video
