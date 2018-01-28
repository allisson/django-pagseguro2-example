from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import CartItemForm
from .models import Event, Cart, Purchase


@login_required
def event_list(request):
    events = Event.objects.all()
    context = {
        'events': events,
        'cart': Cart.objects.get_cart_for_user(request.user)
    }
    return render(request, 'tickets/event_list.html', context=context)


@login_required
def event_detail(request, id):
    event = get_object_or_404(Event, id=id)
    context = {
        'event': event,
        'cart': Cart.objects.get_cart_for_user(request.user)
    }
    return render(request, 'tickets/event_detail.html', context=context)


@login_required
def cart_detail(request):
    context = {
        'cart': Cart.objects.get_cart_for_user(request.user)
    }
    return render(request, 'tickets/cart_detail.html', context=context)


@login_required
@require_http_methods(['POST'])
def cart_clear(request):
    cart = Cart.objects.get_cart_for_user(request.user)
    cart.cart_items.all().delete()
    return redirect(reverse('tickets:cart_detail'))


@login_required
@require_http_methods(['POST'])
def cart_add_item(request):
    cart = Cart.objects.get_cart_for_user(request.user)
    form = CartItemForm(request.POST)
    if form.is_valid():
        ticket = form.cleaned_data.get('ticket')
        quantity = form.cleaned_data.get('quantity')
        Cart.objects.add_cart_item(cart, ticket, quantity)
    return redirect(reverse('tickets:cart_detail'))


@login_required
@require_http_methods(['POST'])
@transaction.atomic
def purchase_create(request):
    cart = Cart.objects.get_cart_for_user(request.user)
    purchase = Purchase.objects.create_checkout(cart)
    return redirect(reverse('tickets:purchase_detail', args=[purchase.id]))


@login_required
def purchase_list(request):
    purchases = Purchase.objects.filter(user=request.user)
    context = {'purchases': purchases}
    return render(request, 'tickets/purchase_list.html', context=context)


@login_required
def purchase_detail(request, id):
    purchase = get_object_or_404(Purchase, id=id, user=request.user)
    context = {'purchase': purchase}
    return render(request, 'tickets/purchase_detail.html', context=context)
