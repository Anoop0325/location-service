import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import UserLocation

class NewsLocationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.news_url = reverse('news_detail')
        self.save_url = reverse('save_location')

    def test_news_detail_view(self):
        """Test that the news detail page loads successfully and uses the correct template."""
        response = self.client.get(self.news_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/news_detail.html')

    def test_save_location_invalid_method(self):
        """Test that requesting with GET on the API endpoint returns 405."""
        response = self.client.get(self.save_url)
        self.assertEqual(response.status_code, 405)

    def test_save_location_missing_coordinates(self):
        """Test that missing coordinates returns a 400 error."""
        data = {'accuracy': 15.0}
        response = self.client.post(
            self.save_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Missing coordinates')

    def test_save_location_invalid_json(self):
        """Test that sending invalid JSON syntax returns a 400 error."""
        response = self.client.post(
            self.save_url,
            data="invalid-json-content",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')

    def test_save_location_success(self):
        """Test successfully saving coordinates with client IP and User-Agent metadata."""
        data = {
            'latitude': 28.5284345,
            'longitude': 77.2584954,
            'accuracy': 22.5
        }
        user_agent_str = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
        
        response = self.client.post(
            self.save_url,
            data=json.dumps(data),
            content_type='application/json',
            HTTP_USER_AGENT=user_agent_str,
            REMOTE_ADDR="192.168.1.50"
        )
        
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'success')
        self.assertIn('id', response_json)

        # Check database persistence
        db_location = UserLocation.objects.get(id=response_json['id'])
        self.assertAlmostEqual(float(db_location.latitude), 28.5284345)
        self.assertAlmostEqual(float(db_location.longitude), 77.2584954)
        self.assertEqual(db_location.accuracy, 22.5)
        self.assertEqual(db_location.user_agent, user_agent_str)
        self.assertEqual(db_location.ip_address, "192.168.1.50")

    def test_live_locations_dashboard(self):
        """Test that the live locations dashboard loads successfully and has session variables."""
        UserLocation.objects.create(
            latitude=28.5284345,
            longitude=77.2584954,
            accuracy=10.0,
            session_id='test-session-123'
        )
        url = reverse('live_locations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/live_locations.html')
        self.assertIn('sessions', response.context)
        self.assertEqual(len(response.context['sessions']), 1)
        self.assertEqual(response.context['sessions'][0]['session_id'], 'test-session-123')

    def test_api_session_details(self):
        """Test retrieving the coordinate list for a specific session ID."""
        UserLocation.objects.create(
            latitude=28.5284,
            longitude=77.2584,
            accuracy=15.0,
            session_id='test-session-999'
        )
        url = reverse('api_session_details', kwargs={'session_id': 'test-session-999'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'success')
        self.assertEqual(len(response_json['locations']), 1)
        self.assertEqual(response_json['locations'][0]['latitude'], 28.5284)

