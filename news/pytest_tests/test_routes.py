import pytest
from pytest_django.asserts import assertRedirects

from http import HTTPStatus

from django.urls import reverse
from news.models import News, Comment

COMMENT_TEXT = 'Текст комментария'

pytestmark = pytest.mark.django_db


# Проверка доступа анонима к главноей страницы, входа/выхода и регистрации
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# Проверка доступности detail анонимому
@pytest.mark.parametrize(
    'name',
    ('news:detail',)
)
def test_detail_availability_for_anonymous_user(client, name, news):
    url = reverse(name, args=(news.pk,))  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# Редактирование и удаление комментария для автора
def test_pages_availability_edit_comment_for_author(author_client,
                                                    comment,
                                                    edit_url,
                                                    form_data,
                                                    url_to_comments):
    """Тест автор может редактировать свой комментарий."""
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
