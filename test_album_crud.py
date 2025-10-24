from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Souvenir, AlbumSouvenir

User = get_user_model()


class AlbumCRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create some test souvenirs
        self.souvenir1 = Souvenir.objects.create(
            utilisateur=self.user,
            titre='Test Memory 1',
            description='A test memory',
            date_evenement='2024-01-01'
        )
        self.souvenir2 = Souvenir.objects.create(
            utilisateur=self.user,
            titre='Test Memory 2',
            description='Another test memory',
            date_evenement='2024-01-02'
        )

    def test_album_creation(self):
        """Test creating a new album"""
        response = self.client.post(reverse('core:creer_album'), {
            'titre': 'Test Album',
            'description': 'A test album',
            'souvenirs': [self.souvenir1.id, self.souvenir2.id]
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Check album was created
        album = AlbumSouvenir.objects.get(titre='Test Album')
        self.assertEqual(album.description, 'A test album')
        album_souvenirs = list(album.souvenirs.all())
        self.assertEqual(len(album_souvenirs), 2)
        self.assertIn(self.souvenir1, album_souvenirs)
        self.assertIn(self.souvenir2, album_souvenirs)

    def test_album_detail_view(self):
        """Test viewing album details"""
        album = AlbumSouvenir.objects.create(
            utilisateur=self.user,
            titre='Test Album',
            description='A test album'
        )
        album.souvenirs.add(self.souvenir1, self.souvenir2)

        response = self.client.get(reverse('core:detail_album', args=[album.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Album')
        self.assertContains(response, 'Test Memory 1')
        self.assertContains(response, 'Test Memory 2')

    def test_album_update(self):
        """Test updating an album"""
        album = AlbumSouvenir.objects.create(
            utilisateur=self.user,
            titre='Original Album',
            description='Original description'
        )
        album.souvenirs.add(self.souvenir1)

        response = self.client.post(reverse('core:modifier_album', args=[album.id]), {
            'titre': 'Updated Album',
            'description': 'Updated description',
            'souvenirs': [self.souvenir2.id]
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Check album was updated
        album.refresh_from_db()
        self.assertEqual(album.titre, 'Updated Album')
        self.assertEqual(album.description, 'Updated description')
        self.assertEqual(list(album.souvenirs.all()), [self.souvenir2])

    def test_album_delete(self):
        """Test deleting an album"""
        album = AlbumSouvenir.objects.create(
            utilisateur=self.user,
            titre='Album to Delete',
            description='Will be deleted'
        )

        response = self.client.post(reverse('core:supprimer_album', args=[album.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after success

        # Check album was deleted
        with self.assertRaises(AlbumSouvenir.DoesNotExist):
            AlbumSouvenir.objects.get(id=album.id)

    def test_album_list_view(self):
        """Test viewing the album list"""
        AlbumSouvenir.objects.create(
            utilisateur=self.user,
            titre='Album 1',
            description='First album'
        )
        AlbumSouvenir.objects.create(
            utilisateur=self.user,
            titre='Album 2',
            description='Second album'
        )

        response = self.client.get(reverse('core:liste_albums'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Album 1')
        self.assertContains(response, 'Album 2')