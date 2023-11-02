from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse

from news.models import Comment, News

pytestmark = pytest.mark.django_db


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def edit_url(comment):
    """Урл редактирования комментария."""
    edit_url = reverse('news:edit', args=(comment.id,))
    return edit_url


@pytest.fixture
def delete_url(comment):
    """Урл удаления комментария."""
    delete_url = reverse('news:delete', args=(comment.id,))
    return delete_url


@pytest.fixture
def url_to_comments(news):
    """Урл блока с комментариями."""
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    return url_to_comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
        }


@pytest.fixture
def all_news():

    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def comment_in_cycle(news, author):
    now = datetime.now()
    for index in range(2):
        comment = Comment.objects.create(
        news=news, author=author, text=f'Tекст {index}',
        )
    comment.created = now + timedelta(days=index)
    comment.save()
    return comment


@pytest.fixture
def bad_words_data():
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}