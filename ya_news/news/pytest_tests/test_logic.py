from django.urls import reverse

import pytest

from news.models import Comment


def test_anonymous_user_cant_post_comment(client, news):
    form_data = {
        'news': news,
        'text': 'Test',
    }
    url = reverse('news:detail', args=(news.id,))
    comment_count = (Comment
                     .objects
                     .select_related('news')
                     .filter(news=news)
                     .count())
    client.post(url, data=form_data)
    actual_count = (Comment
                    .objects
                    .select_related('news')
                    .filter(news=news)
                    .count())
    assert comment_count == actual_count


def test_autorized_user_can_post_comment(news, author_client):
    form_data = {
        'news': news,
        'text': 'Test',
    }
    url = reverse('news:detail', args=(news.id,))
    comment_count = (Comment
                     .objects
                     .select_related('news')
                     .filter(news=news)
                     .count())
    author_client.post(url, data=form_data)
    actual_count = (Comment
                    .objects
                    .select_related('news')
                    .filter(news=news)
                    .count())
    assert comment_count != actual_count


def test_bad_words_filter(news, author_client):
    form_data = {
        'news': news,
        'text': 'Редиска - мой любимый овощ'
    }
    url = reverse('news:detail', args=(news.id,))
    comment_count = (Comment
                     .objects
                     .select_related('news')
                     .filter(news=news)
                     .count())
    response = author_client.post(url, data=form_data)
    actual_count = (Comment
                    .objects
                    .select_related('news')
                    .filter(news=news)
                    .count())
    assert ['Не ругайтесь!'] == response.context['form'].errors['text']
    assert comment_count == actual_count


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_authorized_user_can_edit_and_delete(name,
                                             author_client,
                                             comment,
                                             news):
    url = reverse(name, args=(comment.id,))
    if name == 'news:edit':
        old_comment_text = Comment.objects.get(id=comment.id)
        form_data = {
            'news': news,
            'text': 'hello'
        }
        author_client.post(url, data=form_data)
        actual_count = Comment.objects.get(id=comment.id)
        assert actual_count.text != old_comment_text.text
    else:
        comment_count = Comment.objects.filter(id=comment.id).count()
        author_client.post(url)
        actual_count = Comment.objects.filter(id=comment.id).count()
        assert comment_count != actual_count


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_anonymous_user_cant_edit_and_delete(name,
                                             client,
                                             comment,
                                             news):
    url = reverse(name, args=(comment.id,))
    if name == 'news:edit':
        old_comment_text = Comment.objects.get(id=comment.id)
        form_data = {
            'news': news,
            'text': 'hello'
        }
        client.post(url, data=form_data)
        actual_count = Comment.objects.get(id=comment.id)
        assert actual_count.text == old_comment_text.text
    else:
        comment_count = Comment.objects.filter(id=comment.id).count()
        client.post(url)
        actual_count = Comment.objects.filter(id=comment.id).count()
        assert comment_count == actual_count


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_not_author_user_cant_edit_and_delete(name,
                                              not_author_client,
                                              comment,
                                              news):
    url = reverse(name, args=(comment.id,))
    if name == 'news:edit':
        old_comment_text = Comment.objects.get(id=comment.id)
        form_data = {
            'news': news,
            'text': 'hello'
        }
        not_author_client.post(url, data=form_data)
        actual_count = Comment.objects.get(id=comment.id)
        assert actual_count.text == old_comment_text.text
    else:
        comment_count = Comment.objects.filter(id=comment.id).count()
        not_author_client.post(url)
        actual_count = Comment.objects.filter(id=comment.id).count()
        assert comment_count == actual_count
