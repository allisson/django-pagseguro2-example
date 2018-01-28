from decimal import Decimal

import pytest

from apps.tickets.models import Event, Ticket, Cart, CartItem, Purchase


@pytest.fixture
def event():
    return Event.objects.create(title='My Event Title', description='My Event Description')


@pytest.fixture
def ticket(event):
    return Ticket.objects.create(event=event, title='My Ticket Title', price=Decimal('100.00'))


@pytest.fixture
def user(admin_user):
    return admin_user


@pytest.fixture
def cart(user):
    return Cart.objects.create(user=user, closed=False)


@pytest.fixture
def cart_item(cart, ticket):
    return CartItem.objects.create(cart=cart, ticket=ticket, quantity=1, unit_price=Decimal('100.00'))


@pytest.fixture
def purchase(cart_item):
    cart = cart_item.cart
    return Purchase.objects.create(user=cart.user, cart=cart, price=cart.price)


@pytest.fixture
def pagseguro_checkout_response():
    return '''<?xml version="1.0"?>
    <checkout>
      <code>36BCD3B352526D1EE4D6FFA359934D7E</code>
      <date>2018-01-27T10:11:28.000-02:00</date>
    </checkout>
    '''


@pytest.fixture
def pagseguro_checkout_error_response():
    return '''<?xml version="1.0"?>
    <errors>
      <error>
        <code>11029</code>
        <message>Some Error</message>
      </error>
    </errors>
    '''
