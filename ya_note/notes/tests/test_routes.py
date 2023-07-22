from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_author = User.objects.create(username='Testuser')
        cls.user_not_author = User.objects.create(username='NotAuthor')
        cls.note = Note.objects.create(title='Title', text='Text',
                                       author=cls.user_author)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.not_author_client = Client()
        self.authorized_client.force_login(self.user_author)
        self.not_author_client.force_login(self.user_not_author)

    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_auth_user(self):
        urls = ('notes:list', 'notes:success', 'notes:add')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_author_404(self):
        urls = (
            ('notes:detail', (self.note.id,)),
            ('notes:edit', (self.note.id,)),
            ('notes:delete', (self.note.id,)),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.not_author_client.get(url)
                self.assertEqual(response.status_code, 404)

    def test_guest_user_redirect(self):
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.note.id,)),
            ('notes:edit', (self.note.id,)),
            ('notes:delete', (self.note.id,)),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'/auth/login/?next={url}'
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_guest_registration(self):
        urls = (
            '/auth/login/',
            '/auth/logout/',
            '/auth/signup/',
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_user_registration(self):
        urls = (
            '/auth/login/',
            '/auth/logout/',
            '/auth/signup/',
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
