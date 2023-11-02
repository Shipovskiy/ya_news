from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

# Количество новостей на главной странице — не более 10.
@pytest.mark.parametrize(
    'name',
    ('news:home',)
)
def test_news_count(news, name, client, all_news):
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


# Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка.
@pytest.mark.parametrize(
    'name',
    ('news:home',)
)
def test_news_order(news, name, client, all_news):
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


# Комментарии на странице отдельной новости отсортированы 
# в хронологическом порядке: старые в начале списка, новые — в конце.
@pytest.mark.parametrize(
    'name',
    ('news:detail',)
)
def test_comments_order(news, name, author_client, comment_in_cycle):
    url = reverse(name, args=(news.pk,))
    response = author_client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created, all_comments[1].created


# Анонимному пользователю недоступна форма для отправки комментария на
# странице отдельной новости, а авторизованному доступна.
@pytest.mark.parametrize(
    'parametrized_client, form',(
    (pytest.lazy_fixture('client'), False),
    (pytest.lazy_fixture('admin_client'), True),
    )
)
def test_form_or_not_form(news, parametrized_client, form):
    url = reverse('news:detail', args=(news.pk,))
    response = parametrized_client.get(url)
    assert form in response.context
