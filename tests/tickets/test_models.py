import uuid
from decimal import Decimal

import pytest
import responses

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
