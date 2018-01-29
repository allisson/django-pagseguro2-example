from django.contrib import admin

from .models import Event, Ticket, Cart, CartItem, Purchase


class TicketInline(admin.TabularInline):
    model = Ticket


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'created_at')
    inlines = [
        TicketInline,
    ]


class CartItemInline(admin.TabularInline):
    model = CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'closed', 'created_at')
    inlines = [
        CartItemInline,
    ]


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cart', 'price', 'status', 'created_at')


admin.site.register(Event, EventAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Purchase, PurchaseAdmin)
