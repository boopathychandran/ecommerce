from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from . import views
from django.shortcuts import redirect
from .views import CustomLogoutView
from django.contrib import admin

urlpatterns = [
    path('', lambda request: redirect('login'), name='home'),  # Redirect root to login
    
    # Modern Templates (Default)
    path('login/', LoginView.as_view(template_name='login/login_modern.html'), name='login'),
    path('ecommerce/', views.ecommerce_view, name='ecommerce'),
    
    # Legacy Templates removed to avoid duplicate/unused routes
    # (classic login and classic ecommerce routes removed)
    
    # Other Routes
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('buy-now/<slug:slug>/', views.buy_now, name='buy_now'),
    path('cart/', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('ajax/add_to_cart/<slug:slug>/', views.ajax_add_to_cart, name='ajax_add_to_cart'),
    path('ajax/add_to_wishlist/<slug:slug>/', views.ajax_add_to_wishlist, name='ajax_add_to_wishlist'),
    path('ajax/move_to_cart/<slug:slug>/', views.ajax_move_to_cart, name='ajax_move_to_cart'),
    path('ajax/move_all_to_cart/', views.ajax_move_all_to_cart, name='ajax_move_all_to_cart'),
    path('ajax/update_cart_quantity/<slug:slug>/<str:action>/', views.ajax_update_cart_quantity, name='ajax_update_cart_quantity'),
    path('ajax/search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('payment/', views.payment_view, name='payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('address/', views.address_view, name='address'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='login/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='login/password_change_done.html'), name='password_change_done'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(template_name='login/password_change.html'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='login/password_change_done.html'), name='password_change_done'),
]