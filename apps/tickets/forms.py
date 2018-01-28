from django.forms import ModelForm

from .models import CartItem


class CartItemForm(ModelForm):
    class Meta:
        model = CartItem
        fields = ('ticket', 'quantity')
