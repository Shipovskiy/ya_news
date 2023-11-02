from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News

pytestmark = pytest.mark.django_db



 # Анонимный пользователь не может отправить комментарий.
@pytest.mark.parametrize(
    'name',
    ('news:detail',)
)
def test_anonymous_user_cant_create_comment(client, form_data, name, news):
    url = reverse(name, args=(news.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


# Авторизованный пользователь может отправить комментарий.
def test_user_can_create_comment(author_client, author, form_data, url_to_comments):
    response = author_client.post(url_to_comments, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


# Если комментарий содержит запрещённые слова, он не будет опубликован, а форма вернёт ошибку.
def test_user_cant_use_bad_words(author_client, author, form_data, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


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


# Авторизованный пользователь может редактировать или удалять свои комментари, но
# не может редактировать или удалять чужие комментарии.
@pytest.mark.parametrize(
    'name',
    ('news:edit',)
)
def test_pages_availability_edit_for_author(admin_client,
                                            comment,
                                            name,
                                            form_data,
                                            url_to_comments):
    url = reverse(name, args=(comment.pk,))
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


@pytest.mark.parametrize(
    'name',
    ('news:delete',)
)
def test_author_can_delete_comment(author_client,
                                            comment,
                                            name,
                                            form_data,
                                            url_to_comments):
        url = reverse(name, args=(comment.pk,))
        response = author_client.delete(url)
        assertRedirects(response, url_to_comments)
        comments_count = Comment.objects.count()
        assert comments_count == 0


@pytest.mark.parametrize(
    'name',
    ('news:delete',)
)
def test_user_cant_delete_comment_of_another_user(admin_client,
                                            comment,
                                            name,
                                            form_data,
                                            url_to_comments):
        url = reverse(name, args=(comment.pk,))
        response = admin_client.delete(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        comments_count = Comment.objects.count()
        assert comments_count == 1
