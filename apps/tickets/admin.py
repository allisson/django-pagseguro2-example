from django.contrib import admin

from .models import Event, Ticket, Cart, CartItem, Purchase


class TicketInline(admin.TabularInline):
    model = Ticket


class EventAdmin(admin.ModelAdmin):
    inlines = [
        TicketInline,
    ]


class CartItemInline(admin.TabularInline):
    model = CartItem


class CartAdmin(admin.ModelAdmin):
    inlines = [
        CartItemInline,
    ]


admin.site.register(Event, EventAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Purchase)
