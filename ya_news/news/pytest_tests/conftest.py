from datetime import datetime, timedelta

import pytest

from news.models import News, Comment

MODEL_COUNT = 15


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def not_author(django_user_model, db):
    return django_user_model.objects.create(username='Not_Author')


@pytest.fixture
def news(db):
    return News.objects.create(title='title',
                               text='text')


@pytest.fixture
def news_list(db):
    all_news = []
    now = datetime.now()
    for index in range(MODEL_COUNT):
        news = News(title=f'Новость {index}', text='Just a text')
        news.date = now + timedelta(days=index)
        all_news.append(news)
    return News.objects.bulk_create(all_news)


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author, client):
    client.force_login(not_author)
    return client


@pytest.fixture
def comment(author, news, db):
    return Comment.objects.create(news=news, author=author, text='text')
