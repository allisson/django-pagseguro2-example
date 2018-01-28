import pytest
import responses
import status
from django.urls import reverse

from apps.tickets.models import Purchase

pytestmark = pytest.mark.django_db


def test_event_list(admin_client, event):
    url = reverse('tickets:event_list')
    response = admin_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'cart' in response.context
    assert event in response.context['events']


def test_event_detail(admin_client, event):
    url = reverse('tickets:event_detail', args=[event.id])
    response = admin_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'cart' in response.context
    assert response.context['event'] == event


def test_cart_detail(admin_client):
    url = reverse('tickets:cart_detail')
    response = admin_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'cart' in response.context


def test_cart_clear(admin_client, admin_user, cart_item):
    url = reverse('tickets:cart_clear')
    cart = cart_item.cart
    assert cart.cart_items.count() == 1
    response = admin_client.post(url, follow=True)
    assert response.status_code == status.HTTP_200_OK
    assert cart.cart_items.count() == 0


def test_cart_add_item(admin_client, cart, ticket):
    url = reverse('tickets:cart_add_item')
    assert cart.cart_items.count() == 0
    response = admin_client.post(url, {'ticket': ticket.id, 'quantity': 1}, follow=True)
    assert response.status_code == status.HTTP_200_OK
    assert cart.cart_items.count() == 1


@responses.activate
def test_purchase_create(admin_client, cart_item, pagseguro_checkout_response):
    responses.add(
        responses.POST,
        'https://ws.sandbox.pagseguro.uol.com.br/v2/checkout',
        body=pagseguro_checkout_response,
        status=200
    )
    url = reverse('tickets:purchase_create')
    response = admin_client.post(url, follow=True)
    assert response.status_code == status.HTTP_200_OK
    purchase = Purchase.objects.filter(user=cart_item.cart.user).first()
    assert purchase.status == 'pending'
    assert purchase.pagseguro_redirect_url


def test_purchase_list(admin_client, purchase):
    url = reverse('tickets:purchase_list')
    response = admin_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert purchase in response.context['purchases']


def test_purchase_detail(admin_client, purchase):
    url = reverse('tickets:purchase_detail', args=[purchase.id])
    response = admin_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.context['purchase'] == purchase
