from random import choice

from django.urls import reverse

from news.forms import BAD_WORDS
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
    assert comment_count + 1 == actual_count


def test_bad_words_filter(news, author_client):
    bad_word = choice(BAD_WORDS)
    form_data = {
        'news': news,
        'text': f'Почему нельзя говорить {bad_word}?'
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
    assert 'Не ругайтесь!' == response.context['form'].errors['text'][0]
    assert comment_count == actual_count


def test_authorized_user_can_edit(author_client,
                                  comment,
                                  news):
    url = reverse('news:edit', args=(comment.id,))
    old_comment_text = Comment.objects.get(id=comment.id)
    form_data = {
        'news': news,
        'text': 'hello'
    }
    author_client.post(url, data=form_data)
    actual_count = Comment.objects.get(id=comment.id)
    assert actual_count.text != old_comment_text.text


def test_authorized_user_can_delete(author_client,
                                    comment):
    url = reverse('news:delete', args=(comment.id,))
    comment_count = Comment.objects.filter(id=comment.id).count()
    author_client.post(url)
    actual_count = Comment.objects.filter(id=comment.id).count()
    assert comment_count == actual_count + 1


def test_anonymous_user_cant_edit(client, comment, news):
    url = reverse('news:edit', args=(comment.id,))
    old_comment_text = Comment.objects.get(id=comment.id)
    form_data = {
        'news': news,
        'text': 'hello'
    }
    client.post(url, data=form_data)
    actual_count = Comment.objects.get(id=comment.id)
    assert actual_count.text == old_comment_text.text


def test_anonymous_user_cant_delete(client, comment):
    comment_count = Comment.objects.filter(id=comment.id).count()
    client.post('news:delete', args=(comment.id,))
    actual_count = Comment.objects.filter(id=comment.id).count()
    assert comment_count == actual_count


def test_not_author_user_cant_edit(not_author_client, comment, news):
    url = reverse('news:edit', args=(comment.id,))
    old_comment_text = Comment.objects.get(id=comment.id)
    form_data = {
        'news': news,
        'text': 'hello'
    }
    not_author_client.post(url, data=form_data)
    actual_count = Comment.objects.get(id=comment.id)
    assert actual_count.text == old_comment_text.text


def test_not_author_user_cant_delete(not_author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    comment_count = Comment.objects.filter(id=comment.id).count()
    not_author_client.post(url)
    actual_count = Comment.objects.filter(id=comment.id).count()
    assert comment_count == actual_count
