import pytest
from django.urls import reverse

from news.models import News, Comment

COMMENT_TEXT = 'Текст коментария'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def comment():
    comment = Comment.objects.create(
        text='Текст коментария',
    )
    return comment


@pytest.fixture
def edit_url(comment):
    """Урл редактирования комментария."""
    edit_url = reverse('news:edit', args=(comment.pk,))
    return edit_url


@pytest.fixture
def delete_url(comment):
    """Урл удаления комментария."""
    delete_url = reverse('news:delete', args=(comment.pk,))
    return delete_url


@pytest.fixture
def url_to_comments(news):
    """Урл блока с комментариями."""
    url_to_comments = reverse('news:detail', args=(news.pk,)) + '#comments'
    return url_to_comments


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
        }
