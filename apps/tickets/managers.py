from django.db.models import Manager

from pagseguro.api import PagSeguroItem, PagSeguroApi

from .exceptions import CheckoutException


class CartManager(Manager):
    def get_cart_for_user(self, user):
        cart = self.filter(user=user, closed=False).first()
        if not cart:
            self.create(user=user, closed=False)
        return cart

    def add_cart_item(self, cart, ticket, quantity):
        cart_item = cart.cart_items.filter(cart=cart, ticket=ticket).first()
        if cart_item:
            cart_item.quantity += quantity
            cart_item.unit_price = ticket.price
            cart_item.save()
            return cart_item
        return cart.cart_items.create(cart=cart, ticket=ticket, quantity=quantity, unit_price=ticket.price)


class PurchaseManager(Manager):
    def create_purchase(self, cart):
        return self.create(user=cart.user, cart=cart, price=cart.price)

    def create_checkout(self, cart):
        purchase = self.create_purchase(cart)
        pagseguro_api = PagSeguroApi(reference=str(purchase.id))
        for cart_item in cart.cart_items.all():
            ticket = cart_item.ticket
            item = PagSeguroItem(
                id=str(ticket.id),
                description=ticket.title,
                amount=str(cart_item.unit_price),
                quantity=cart_item.quantity
            )
            pagseguro_api.add_item(item)
        pagseguro_data = pagseguro_api.checkout()
        if pagseguro_data['success'] is False:
            raise CheckoutException(pagseguro_data['message'])
        purchase.pagseguro_redirect_url = pagseguro_data['redirect_url']
        purchase.save()
        cart.closed = True
        cart.save()
        return purchase

    def update_purchase_status(self, pagseguro_transaction):
        status_map = {
            '3': 'paid',
            '7': 'canceled'
        }
        purchase = self.filter(id=pagseguro_transaction['reference']).first()
        if not purchase:
            return
        if pagseguro_transaction['status'] not in ('3', '7'):
            return purchase
        purchase.status = status_map[pagseguro_transaction['status']]
        purchase.save()
        return purchase
