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

    def test_home_lists_and_searches_own_requests(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.request.title)

        response = self.client.get(reverse('home'), {'q': 'stairwell'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.request.title)

        response = self.client.get(reverse('home'), {'q': 'Block A'})
        self.assertContains(response, self.request.title)

    def test_home_does_not_expose_other_users_requests(self):
        other_user = get_user_model().objects.create_user(
            username='bob',
            email='bob@example.com',
            password='secret123',
        )
        MaintenanceRequest.objects.create(
            user=other_user,
            title='Private broken window',
            description='A window needs repair.',
            category='other',
            location='Block B',
            priority='low',
            status='pending',
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'), {'q': 'window'})
        self.assertNotContains(response, 'Private broken window')

    def test_staff_can_search_all_tickets_by_requester(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('home'), {'q': 'alice'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.request.title)

    def test_staff_sees_tickets_from_all_users(self):
        other_user = get_user_model().objects.create_user(
            username='bob',
            email='bob@example.com',
            password='secret123',
        )
        other_request = MaintenanceRequest.objects.create(
            user=other_user,
            title='Other user ticket',
            description='Another issue.',
            category='other',
            location='Block B',
            priority='low',
        )
        self.client.force_login(self.staff)
        response = self.client.get(reverse('home'))
        self.assertContains(response, other_request.title)

    def test_home_filters_by_category_status_and_priority(self):
        self.client.force_login(self.user)
        for field, value in (
            ('category', 'other'),
            ('status', 'completed'),
            ('priority', 'low'),
        ):
            with self.subTest(field=field):
                response = self.client.get(reverse('home'), {field: value})
                self.assertNotContains(response, self.request.title)

    def test_user_can_open_and_edit_own_ticket_on_edit_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('edit_request', args=[self.request.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Save Changes')

        response = self.client.post(reverse('edit_request', args=[self.request.pk]), {
            'title': 'Updated pipe',
            'description': 'Still leaking.',
            'category': 'plumbing',
            'location': 'Block C',
            'priority': 'medium',
        })
        self.assertRedirects(response, reverse('home'))
        self.request.refresh_from_db()
        self.assertEqual(self.request.title, 'Updated pipe')
        self.assertEqual(self.request.location, 'Block C')

    def test_staff_can_edit_any_ticket_and_update_status(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('edit_request', args=[self.request.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.context['form'].fields)

        response = self.client.post(reverse('edit_request', args=[self.request.pk]), {
            'title': self.request.title,
            'description': self.request.description,
            'category': self.request.category,
            'location': self.request.location,
            'priority': self.request.priority,
            'status': 'completed',
        })
        self.assertRedirects(response, reverse('home'))
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'completed')

    def test_user_cannot_edit_another_users_ticket(self):
        other_user = get_user_model().objects.create_user(
            username='bob',
            email='bob@example.com',
            password='secret123',
        )
        other_request = MaintenanceRequest.objects.create(
            user=other_user,
            title='Private request',
            description='Not yours.',
            category='other',
            location='Block B',
            priority='low',
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('edit_request', args=[other_request.pk]))
        self.assertEqual(response.status_code, 404)
        other_request.refresh_from_db()
        self.assertEqual(other_request.title, 'Private request')

    def test_user_can_delete_ticket_from_home(self):
        self.client.force_login(self.user)
        delete_url = reverse('delete_request', args=[self.request.pk])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirm ticket deletion')
        self.assertTrue(MaintenanceRequest.objects.filter(pk=self.request.pk).exists())

        response = self.client.post(delete_url, {
            'confirm': 'yes',
            'filter_q': '',
            'filter_category': '',
            'filter_status': '',
            'filter_priority': '',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(MaintenanceRequest.objects.filter(pk=self.request.pk).exists())

    def test_staff_can_delete_ticket_from_home(self):
        self.client.force_login(self.staff)
        delete_url = reverse('delete_request', args=[self.request.pk])
        response = self.client.post(delete_url, {
            'confirm': 'yes',
            'filter_q': '',
            'filter_category': '',
            'filter_status': '',
            'filter_priority': '',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(MaintenanceRequest.objects.filter(pk=self.request.pk).exists())

    def test_user_cannot_delete_another_users_ticket_from_home(self):
        self.client.force_login(self.user)
        other_user = get_user_model().objects.create_user(
            username='bob',
            email='bob@example.com',
            password='secret123',
        )
        other_ticket = MaintenanceRequest.objects.create(
            user=other_user,
            title='Private ticket',
            description='Another user ticket.',
            category='other',
            location='Block B',
            priority='low',
        )
        response = self.client.get(reverse('delete_request', args=[other_ticket.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(MaintenanceRequest.objects.filter(pk=other_ticket.pk).exists())

    def test_delete_confirmation_rejects_invalid_post(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('delete_request', args=[self.request.pk]), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(MaintenanceRequest.objects.filter(pk=self.request.pk).exists())
