from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Souvenir, AlbumSouvenir, CapsuleTemporelle

User = get_user_model()

class CoreTests(TestCase):
    def setUp(self):
        """Set up test data for all tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_dashboard_access(self):
        """Test dashboard requires login"""
        # Test redirect when not logged in
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)

        # Test access when logged in
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_souvenir_creation(self):
        """Test creating a memory"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(reverse('core:ajouter_souvenir'), {
            'titre': 'Test Memory',
            'description': 'A wonderful test memory about friends',
            'emotion': 'joy',
            'date_evenement': '2024-01-01',
        })

        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Check memory was created
        souvenir = Souvenir.objects.get(titre='Test Memory')
        self.assertEqual(souvenir.utilisateur, self.user)
        self.assertEqual(souvenir.emotion, 'joy')

    def test_album_creation_and_management(self):
        """Test album creation and management"""
        # Create test memories first
        souvenir1 = Souvenir.objects.create(
            utilisateur=self.user,
            titre='Memory 1',
            description='First memory',
            emotion='joy',
            date_evenement='2024-01-01'
        )

        souvenir2 = Souvenir.objects.create(
            utilisateur=self.user,
            titre='Memory 2',
            description='Second memory',
            emotion='nostalgia',
            date_evenement='2024-01-02'
        )

        self.client.login(username='testuser', password='testpass123')

        # Test album creation
        response = self.client.post(reverse('core:creer_album'), {
            'titre': 'Test Album',
            'description': 'Test album description',
            'souvenirs': [souvenir1.id, souvenir2.id]
        })

        self.assertEqual(response.status_code, 302)

        # Check album exists
        album = AlbumSouvenir.objects.get(titre='Test Album')
        self.assertEqual(album.souvenirs.count(), 2)

        # Test album detail view
        response = self.client.get(reverse('core:detail_album', args=[album.id]))
        self.assertEqual(response.status_code, 200)

    def test_time_capsule_creation(self):
        """Test time capsule creation"""
        # Create a memory first
        souvenir = Souvenir.objects.create(
            utilisateur=self.user,
            titre='Capsule Memory',
            description='Memory for time capsule',
            emotion='joy',
            date_evenement='2024-01-01'
        )

        self.client.login(username='testuser', password='testpass123')

        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=30)

        response = self.client.post(reverse('core:creer_capsule'), {
            'titre': 'Test Capsule',
            'description': 'Test capsule description',
            'emotion': 'joy',
            'date_evenement': '2024-01-01',
            'date_ouverture': future_date,
            'message_futur': 'Hello future me!'
        })

        self.assertEqual(response.status_code, 302)

        # Check capsule was created
        capsule = CapsuleTemporelle.objects.get(souvenir__titre='Test Capsule')
        self.assertEqual(capsule.souvenir.utilisateur, self.user)
        self.assertFalse(capsule.is_opened)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_flow(self):
        """Test password reset functionality"""
        from django.core import mail

        # Test password reset request
        response = self.client.post(reverse('password_reset'), {
            'email': 'test@example.com'
        })

        self.assertEqual(response.status_code, 302)  # Redirect to done page

        # Check email was sent (in test backend)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Password Reset', mail.outbox[0].subject)