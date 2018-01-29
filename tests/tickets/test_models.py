import uuid
from decimal import Decimal

import pytest
import responses
from django.urls import reverse

from apps.tickets.exceptions import CheckoutException
from apps.tickets.models import Cart, CartItem, Purchase

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('model', [
    pytest.lazy_fixture('event'),
    pytest.lazy_fixture('ticket'),
    pytest.lazy_fixture('cart'),
    pytest.lazy_fixture('cart_item'),
    pytest.lazy_fixture('purchase'),
])
def test_model_str_representation(model):
    assert str(model)


@pytest.mark.parametrize('model', [
    pytest.lazy_fixture('event'),
    pytest.lazy_fixture('ticket'),
    pytest.lazy_fixture('cart'),
    pytest.lazy_fixture('cart_item'),
    pytest.lazy_fixture('purchase'),
])
def test_model_id_field(model):
    assert isinstance(model.id, uuid.UUID)


@pytest.mark.parametrize('quantity1,price1,quantity2,price2,expected_price', [
    (1, Decimal('100.00'), 1, Decimal('100.00'), Decimal('200.00')),
    (2, Decimal('100.00'), 2, Decimal('100.00'), Decimal('400.00')),
])
def test_cart_price_property(quantity1, price1, quantity2, price2, expected_price, cart, ticket):
    CartItem.objects.create(cart=cart, ticket=ticket, quantity=quantity1, unit_price=price1)
    CartItem.objects.create(cart=cart, ticket=ticket, quantity=quantity2, unit_price=price2)
    assert cart.price == expected_price


def test_cart_manager_get_cart_for_user(cart, user):
    cart = Cart.objects.get_cart_for_user(user)
    assert cart.user == user
    assert cart.closed is False
    assert Cart.objects.get_cart_for_user(user) == cart

    cart.closed = True
    cart.save()
    assert Cart.objects.get_cart_for_user(user) != cart


def test_cart_manager_add_cart_item(cart, ticket):
    quantity = 1
    cart_item = Cart.objects.add_cart_item(cart, ticket, quantity)
    assert cart_item.cart == cart
    assert cart_item.ticket == ticket
    assert cart_item.quantity == quantity
    assert cart_item.unit_price == ticket.price

    cart_item = Cart.objects.add_cart_item(cart, ticket, quantity)
    assert cart_item.cart == cart
    assert cart_item.ticket == ticket
    assert cart_item.quantity == quantity + 1
    assert cart_item.unit_price == ticket.price


@pytest.mark.parametrize('quantity,price,expected_price', [
    (1, Decimal('100.00'), Decimal('100.00')),
    (2, Decimal('100.00'), Decimal('200.00')),
])
def test_cart_item_price_property(quantity, price, expected_price, cart, ticket):
    cart_item = CartItem.objects.create(cart=cart, ticket=ticket, quantity=quantity, unit_price=price)
    assert cart_item.price == expected_price


def test_purchase_manager_create_purchase(cart):
    purchase = Purchase.objects.create_purchase(cart)
    assert purchase.user == cart.user
    assert purchase.cart == cart
    assert purchase.price == cart.price
    assert purchase.status == 'pending'
    assert purchase.pagseguro_redirect_url == ''


@responses.activate
def test_purchase_manager_create_checkout(cart_item, pagseguro_checkout_response):
    responses.add(
        responses.POST,
        'https://ws.sandbox.pagseguro.uol.com.br/v2/checkout',
        body=pagseguro_checkout_response,
        status=200
    )
    cart = cart_item.cart
    purchase = Purchase.objects.create_checkout(cart)
    assert purchase.pagseguro_redirect_url == 'https://sandbox.pagseguro.uol.com.br/v2/checkout/payment.html?code=36BCD3B352526D1EE4D6FFA359934D7E'
    assert cart.closed is True


@responses.activate
def test_purchase_manager_create_checkout_with_error(cart_item, pagseguro_checkout_error_response):
    responses.add(
        responses.POST,
        'https://ws.sandbox.pagseguro.uol.com.br/v2/checkout',
        body=pagseguro_checkout_error_response,
        status=400
    )
    cart = cart_item.cart
    with pytest.raises(CheckoutException):
        Purchase.objects.create_checkout(cart)


@pytest.mark.parametrize('pagseguro_status,expected_status', [
    ('2', 'pending'),
    ('3', 'paid'),
    ('4', 'pending'),
    ('5', 'pending'),
    ('6', 'pending'),
    ('7', 'canceled'),
    ('8', 'pending'),
    ('9', 'pending'),
])
def test_purchase_manager_update_purchase_status(pagseguro_status, expected_status, purchase, pagseguro_transaction):
    pagseguro_transaction['reference'] = str(purchase.id)
    pagseguro_transaction['status'] = pagseguro_status
    purchase = Purchase.objects.update_purchase_status(pagseguro_transaction)
    assert purchase.status == expected_status


def test_purchase_manager_update_purchase_status_with_invalid_reference(pagseguro_transaction):
    pagseguro_transaction['reference'] = str(uuid.uuid4())
    assert Purchase.objects.update_purchase_status(pagseguro_transaction) is None


@responses.activate
def test_update_purchase_status(client, purchase, pagseguro_notification, pagseguro_transaction_response):
    pagseguro_transaction_response = pagseguro_transaction_response.replace(
        '<reference>9fd05f66-315c-49f9-85f7-c92775f5a54d</reference>',
        '<reference>{}</reference>'.format(str(purchase.id))
    )
    pagseguro_transaction_response = pagseguro_transaction_response.replace(
        '<status>1</status>', '<status>3</status>'
    )
    code = pagseguro_notification['notificationCode']
    responses.add(
        responses.GET,
        'https://ws.sandbox.pagseguro.uol.com.br/v2/transactions/notifications/{}'.format(code),
        body=pagseguro_transaction_response,
        status=200
    )
    url = reverse('pagseguro_receive_notification')
    client.post(url, pagseguro_notification)
    purchase.refresh_from_db()
    assert purchase.status == 'paid'
