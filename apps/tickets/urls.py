from django.urls import path

from . import views

app_name = 'tickets'
urlpatterns = [
    path('eventos/', views.event_list, name='event_list'),
    path('eventos/<id>/', views.event_detail, name='event_detail'),
    path('carrinho/', views.cart_detail, name='cart_detail'),
    path('carrinho/limpar/', views.cart_clear, name='cart_clear'),
    path('carrinho/adicionar/', views.cart_add_item, name='cart_add_item'),
    path('compras/criar/', views.purchase_create, name='purchase_create'),
    path('compras/', views.purchase_list, name='purchase_list'),
    path('compras/<id>/', views.purchase_detail, name='purchase_detail'),
]
