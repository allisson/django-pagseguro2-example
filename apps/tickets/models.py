import uuid

from django.conf import settings
from django.db import models
from pagseguro.signals import notificacao_recebida

from .managers import CartManager, PurchaseManager


def generate_code():
    return uuid.uuid4()


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=generate_code)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Event(BaseModel):
    title = models.CharField('título', max_length=128)
    description = models.TextField('descrição')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'


class Ticket(BaseModel):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, verbose_name='evento', related_name='tickets')
    title = models.CharField('título', max_length=128)
    price = models.DecimalField('preço', max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = 'ticket'
        verbose_name_plural = 'tickets'


class Cart(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='usuário', related_name='carts')
    closed = models.BooleanField('carrinho finalizado', db_index=True, default=False)
    objects = CartManager()

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'carrinho de compra'
        verbose_name_plural = 'carrinhos de compra'

    @property
    def price(self):
        return sum([cart_item.price for cart_item in self.cart_items.all()])


class CartItem(BaseModel):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, verbose_name='carrinho', related_name='cart_items')
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, verbose_name='ticket', related_name='cart_items')
    quantity = models.SmallIntegerField('quantidade', default=1)
    unit_price = models.DecimalField('preço unitário', max_digits=10, decimal_places=2)

    def __str__(self):
        return '{} - {} - {}'.format(self.cart, self.ticket, self.price)

    class Meta:
        ordering = ['id']
        verbose_name = 'item do carrinho de compra'
        verbose_name_plural = 'itens do carrinho de compra'
        unique_together = ('cart', 'ticket')

    @property
    def price(self):
        return self.quantity * self.unit_price


PURCHASE_STATUS_CHOICES = (
    ('pending', 'Pendente'),
    ('paid', 'Pago'),
    ('canceled', 'Cancelado'),
)


class Purchase(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='usuário', related_name='purchases')
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, verbose_name='carrinho', related_name='purchases')
    price = models.DecimalField('preço', max_digits=10, decimal_places=2)
    status = models.CharField('status da compra', max_length=16, default='pending', choices=PURCHASE_STATUS_CHOICES)
    pagseguro_redirect_url = models.URLField('url do pagseguro', max_length=255, blank=True)
    objects = PurchaseManager()

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'compra'
        verbose_name_plural = 'compras'


def update_purchase_status(sender, transaction, **kwargs):
    Purchase.objects.update_purchase_status(transaction)


notificacao_recebida.connect(update_purchase_status)
