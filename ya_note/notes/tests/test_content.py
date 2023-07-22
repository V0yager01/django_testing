from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user_1 = User.objects.create(username='TestUser1')
        cls.test_user_2 = User.objects.create(username='TestUser2')
        cls.note = Note.objects.create(title='title',
                                       text='text',
                                       author=cls.test_user_1)

    def setUp(self):
        self.user_1 = Client()
        self.user_2 = Client()
        self.user_1.force_login(self.test_user_1)
        self.user_2.force_login(self.test_user_2)

    def test_note_in_context(self):
        response = self.user_1.get(reverse('notes:list'))
        self.assertIn(self.note, response.context['object_list'])

    def test_note_not_in_not_author_list(self):
        response = self.user_2.get(reverse('notes:list'))
        self.assertNotIn(self.note, response.context['object_list'])

    def test_forms(self):
        forms = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in forms:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.user_1.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
