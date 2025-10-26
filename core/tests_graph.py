from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Note, Link
import uuid


class GraphAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='graphuser', password='pass')
        self.client = Client()
        self.client.force_login(self.user)

        # Create notes
        self.note1 = Note.objects.create(owner=self.user, title='Note A', body='Content A')
        self.note2 = Note.objects.create(owner=self.user, title='Note B', body='Content B')
        Link.objects.create(src=self.note1, dst=self.note2)

    def test_graph_api(self):
        resp = self.client.get('/graph/api/graph/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('nodes', data)
        self.assertIn('edges', data)
        self.assertGreaterEqual(len(data['nodes']), 2)

    def test_note_detail_api(self):
        resp = self.client.get(f'/graph/api/notes/{self.note1.id}/')
        self.assertEqual(resp.status_code, 200)
        note = resp.json()
        self.assertEqual(note['title'], 'Note A')
