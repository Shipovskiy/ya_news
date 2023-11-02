import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse
from http import HTTPStatus


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
@pytest.mark.parametrize(
    'name',
    ('news:edit',)
)
def test_pages_availability_edit_for_author(author_client,
                                            comment,
                                            name,
                                            form_data,
                                            url_to_comments):
    url = reverse(name, args=(comment.pk,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == 'Новый текст'


# Страницы удаления и редактирования комментария доступны автору комментария,
# другому пользователю не доступны.
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


# При попытке перейти на страницу редактирования или удаления комментария
# анонимный пользователь перенаправляется на страницу авторизации.
@pytest.mark.parametrize(
    'name, comment_object',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    ),
)
def test_redirects(client, name, comment_object):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment_object.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
