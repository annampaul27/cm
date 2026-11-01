from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MaintenanceRequest


class MaintenanceRequestViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='alice',
            email='alice@example.com',
            password='secret123',
        )
        self.staff = get_user_model().objects.create_user(
            username='staff',
            email='staff@example.com',
            password='secret123',
            is_staff=True,
        )
        self.request = MaintenanceRequest.objects.create(
            user=self.user,
            title='Broken pipe',
            description='Hot water pipe leaking by the stairwell.',
            category='plumbing',
            location='Block A',
            priority='high',
            status='pending',
        )

    def test_my_requests_includes_filter_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('my_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('filter_form', response.context)

    def test_staff_status_page_includes_maintenance_request(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('staff_update_status', args=[self.request.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('maintenance_request', response.context)
        self.assertEqual(response.context['maintenance_request'], self.request)

    def test_request_detail_page_renders(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('request_detail', args=[self.request.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.request.title)

    def test_staff_can_delete_request_from_dashboard(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('staff_delete_request', args=[self.request.pk]))
        self.assertRedirects(response, reverse('staff_dashboard'))
        self.assertFalse(MaintenanceRequest.objects.filter(pk=self.request.pk).exists())

    def test_non_staff_cannot_delete_request_from_staff_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('staff_delete_request', args=[self.request.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(MaintenanceRequest.objects.filter(pk=self.request.pk).exists())

    def test_staff_delete_requires_post(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('staff_delete_request', args=[self.request.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(MaintenanceRequest.objects.filter(pk=self.request.pk).exists())
