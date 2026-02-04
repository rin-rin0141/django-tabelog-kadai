from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from taberogumodoki.views.account_views import (SignUpView, Login, AccountUpdateView, ProfileView,)
from taberogumodoki.views.cart_views import (CartListView, AddCartView, remove_from_cart,)
from taberogumodoki.views.item_views import (IndexListView, ItemDetailView, CategoryListView, TagListView, SearchView,)
from taberogumodoki.views.order_views import (OrderIndexView, OrderDetailView,)
from taberogumodoki.views.pay_views import (PayWithStripe, PaySuccessView, PayCancelView, SubscribeCancelView, SubscribeSuccessView,)
from taberogumodoki.views.premium_payment_views import CreateCheckoutSessionView
from taberogumodoki.views.stripe_sent_views import stripe_webhook
from taberogumodoki.views.review_views import create_review  
from taberogumodoki.views.order_views import ReserveView, UnreserveView
from taberogumodoki.views.admin_views import AdminLogoutView

urlpatterns = [
    # Top
    path('', IndexListView.as_view(), name='index'),

    # Account
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('account/', AccountUpdateView.as_view(), name='account'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # Order
    path('orders/', OrderIndexView.as_view(), name='orders'),
    path('orders/<str:pk>/', OrderDetailView.as_view(), name='order_detail'),

    # Pay
    path('pay/checkout/', PayWithStripe.as_view(), name='pay_checkout'),
    path('pay/success/', PaySuccessView.as_view(), name='pay_success'),
    path('pay/cancel/', PayCancelView.as_view(), name='pay_cancel'),

    # Cart
    path('cart/', CartListView.as_view(), name='cart'),
    path('cart/add/', AddCartView.as_view(), name='cart_add'),
    path('cart/remove/<str:pk>/', remove_from_cart, name='cart_remove'),

    # Items
    path('items/<str:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('categories/<str:pk>/', CategoryListView.as_view(), name='category'),
    path('tags/<str:pk>/', TagListView.as_view(), name='tag'),
    path('search/', SearchView.as_view(), name='search'),
    
    # Stripe Webhook
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
    path('subscribe/', CreateCheckoutSessionView.as_view(), name='subscribe'),
    path('subscribe/success/', SubscribeSuccessView.as_view()),
    path('subscribe/cancel/', SubscribeCancelView.as_view(), name='subscribe_cancel'),

    # Reviews
    path('items/<str:item_id>/reviews/create/' ,create_review, name='create_review'),
    
    #予約
    path('items/<str:pk>/reserve/', ReserveView.as_view(), name='reserve'),
    # 予約キャンセル
    path('orders/<str:pk>/unreserve/', UnreserveView.as_view(), name='unreserve'),


]
