from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user_1 = User.objects.create(username='TestUser1')
        cls.test_user_2 = User.objects.create(username='TestUser2')
        cls.note = Note.objects.create(title='title',
                                       text='text',
                                       slug='slug',
                                       author=cls.test_user_1)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.authorized_client = Client()
        self.author_client.force_login(self.test_user_1)
        self.authorized_client.force_login(self.test_user_2)

    def test_authorized_client_add(self):
        form_data = {
            'title': 'Title',
            'text': 'Text',
            'slug': 'Slug123'
        }
        note_count = Note.objects.count()
        self.author_client.post(reverse('notes:add'),
                                data=form_data)
        self.assertEqual(note_count + 1, Note.objects.count())

    def test_guest_client_add(self):
        form_data = {
            'title': 'Title',
            'text': 'Text',
            'slug': 'Slug123'
        }

        note_count = Note.objects.count()
        self.guest_client.post(reverse('notes:add'),
                               data=form_data)
        self.assertEqual(note_count, Note.objects.count())

    def test_slug_error(self):
        form_data = {
            'title': 'title',
            'text': 'Text',
            'slug': 'slug',
        }
        note_count = Note.objects.count()
        response = self.author_client.post(reverse('notes:add'),
                                           data=form_data)
        self.assertFormError(response, 'form', 'slug', 'slug' + WARNING)
        self.assertEqual(Note.objects.count(), note_count)

    def test_slugify(self):
        form_data = {
            'title': 'Титульник',
            'text': 'Text'
        }
        slug = slugify('Титульник')
        self.authorized_client.post(reverse('notes:add'), data=form_data)
        response = self.authorized_client.get(reverse('notes:detail',
                                                      args=(slug,)))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_note_edit(self):
        form_data = {
            'title': 'NewTitle',
            'text': 'Text',
            'slug': 'slug',
        }
        self.author_client.post(reverse('notes:edit',
                                        kwargs={'slug':
                                                self.note.slug}),
                                data=form_data)
        note_edit = Note.objects.get(slug=self.note.slug)
        self.assertEqual(note_edit.title, 'NewTitle')

    def test_not_author_cant_edit(self):
        form_data = {
            'title': 'NewTitle',
            'text': 'Text',
            'slug': 'slug',
        }
        response = self.authorized_client.post(reverse('notes:edit',
                                                       kwargs={'slug':
                                                               self.note
                                                               .slug}),
                                               data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(slug='slug')
        self.assertEqual(note.title, 'title')

    def test_author_can_delete_comment(self):
        old_count = Note.objects.count()
        self.author_client.delete(reverse('notes:delete',
                                          kwargs={'slug': 'slug'}))
        actual_count = Note.objects.count()
        self.assertEqual(old_count, actual_count + 1)

    def test_user_cant_delete_comment_of_another_user(self):
        old_count = Note.objects.count()
        response = self.authorized_client.delete(reverse('notes:delete',
                                                         kwargs={'slug':
                                                                 'slug'}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        actual_count = Note.objects.count()
        self.assertEqual(old_count, actual_count)
