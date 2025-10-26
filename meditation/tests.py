from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import FocusCategory, FocusSession
import json


class FocusAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client = Client()
        self.client.force_login(self.user)
        self.cat = FocusCategory.objects.create(name='Study', color='#FF8C42')

    def test_start_pause_resume_complete_and_stats(self):
        # Start session
        resp = self.client.post('/focus/api/sessions/start/', json.dumps({'category_id': self.cat.id}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        session_id = data.get('session_id')
        self.assertIsNotNone(session_id)

        # Pause
        resp = self.client.post(f'/focus/api/sessions/{session_id}/pause/')
        self.assertEqual(resp.status_code, 200)

        # Resume
        resp = self.client.post(f'/focus/api/sessions/{session_id}/resume/')
        self.assertEqual(resp.status_code, 200)

        # Complete
        resp = self.client.post(f'/focus/api/sessions/{session_id}/complete/', json.dumps({'notes': 'Good work'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('duration', data)

        # Stats
        resp = self.client.get('/focus/api/stats/')
        self.assertEqual(resp.status_code, 200)
        stats = resp.json()
        self.assertIn('today_minutes', stats)
