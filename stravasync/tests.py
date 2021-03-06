from unittest.mock import patch

from django.urls import reverse

from dpnk.test.test_views import ViewsLogon


mock_token_response = {
    "access_token": "123456",
    "refresh_token": "6789",
    "expires_at": 343,
}


class MockAthlete():
    def __init__(self):
        self.username = 'test_strava_user'
        self.firstname = 'John'
        self.lastname = 'Smith'


class TestStravaAuth(ViewsLogon):

    @patch('stravalib.Client')
    def test_strava_auth(self, mock_strava_client):
        msc = mock_strava_client()
        msc.exchange_code_for_token.return_value = mock_token_response
        msc.refresh_access_token.return_value = mock_token_response
        msc.get_athlete.return_value = MockAthlete()
        response = self.client.get(reverse('strava_auth'))
        self.assertRedirects(response, reverse('about_strava'), status_code=302)

    @patch('stravalib.Client')
    def test_about_strava_logged_out(self, mock_strava_client):
        msc = mock_strava_client()
        msc.authorization_url.return_value = "https://strava.com/authorize/url.html"
        response = self.client.get(reverse('about_strava'))
        self.assertContains(
            response,
            '<input type="image" src="/static/img/connect_with_strava.png" alt="Propojit se Stravou" class="btn btn-default float-right"/>',
            html=True,
            status_code=200,
        )

    @patch('stravalib.Client')
    def test_about_strava_logged_in(self, mock_strava_client):
        msc = mock_strava_client()
        msc.exchange_code_for_token.return_value = mock_token_response
        msc.refresh_access_token.return_value = mock_token_response
        msc.get_athlete.return_value = MockAthlete()
        self.client.get(reverse('strava_auth'))
        response = self.client.get(reverse('about_strava'))
        self.assertContains(
            response,
            '<input type="submit" class="btn btn-default float-right" value="Synchronizovat" />',
            html=True,
            status_code=200,
        )

    @patch('stravalib.Client')
    def test_strava_deauth(self, mock_strava_client):
        msc = mock_strava_client()
        msc.exchange_code_for_token.return_value = mock_token_response
        msc.get_athlete.return_value = MockAthlete()
        self.client.get(reverse('strava_auth'))
        response = self.client.post(reverse('strava_deauth'))
        self.assertRedirects(response, reverse('about_strava'), status_code=302)
