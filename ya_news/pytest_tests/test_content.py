from datetime import datetime, timedelta

from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment


NEWS_COUNT = 10


def test_page_contains_ten_news(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    assert len(response.context['object_list']) == NEWS_COUNT


def test_page_contains_sorted_news(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_are_sorted(client, author, news):
    now = datetime.now()
    for index in range(2):
        comment = Comment.objects.create(author=author, text='Just a text',
                                         news=news)
        comment.created = now + timedelta(days=index)
        comment.save()

    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


def test_autorized_client_has_form(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_guest_client_has_not_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context
