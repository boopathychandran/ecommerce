from decimal import Decimal
from django.db import transaction
from django.utils.text import slugify
from .models import Product, Category, Cart, CartItem, Wishlist, Order, OrderItem
import logging

logger = logging.getLogger(__name__)

class CartService:
    @staticmethod
    def get_or_create_cart(user):
        """Get user cart or create one, with basic caching for count"""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def invalidate_cache(user_id):
        from django.core.cache import cache
        cache.delete(f"cart_count_{user_id}")

    @staticmethod
    def add_to_cart(user, product_id, quantity=1):
        product = Product.objects.get(id=product_id)
        if product.stock < quantity:
            return False, "Insufficient stock"
        
        cart = CartService.get_or_create_cart(user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            if product.stock < (item.quantity + quantity):
                return False, "Cannot exceed available stock"
            item.quantity += quantity
        else:
            item.quantity = quantity
        
        item.save()
        CartService.invalidate_cache(user.id)
        return True, "Added to cart"

    @staticmethod
    def remove_from_cart(user, product_id):
        cart = CartService.get_or_create_cart(user)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        CartService.invalidate_cache(user.id)
        return True

    @staticmethod
    def update_quantity(user, product_id, action):
        cart = CartService.get_or_create_cart(user)
        try:
            item = CartItem.objects.get(cart=cart, product_id=product_id)
            if action == 'increase':
                if item.product.stock > item.quantity:
                    item.quantity += 1
                else:
                    return False, "Out of stock"
            elif action == 'decrease':
                if item.quantity > 1:
                    item.quantity -= 1
                else:
                    item.delete()
                    return True, "Item removed"
            item.save()
            CartService.invalidate_cache(user.id)
            return True, "Quantity updated"
        except CartItem.DoesNotExist:
            return False, "Item not in cart"

    @staticmethod
    def move_wishlist_to_cart(user, product_id=None):
        """Move one or all items from wishlist to cart"""
        cart = CartService.get_or_create_cart(user)
        wishlist_query = Wishlist.objects.filter(user=user)
        
        if product_id:
            wishlist_query = wishlist_query.filter(product_id=product_id)
        
        items_moved = 0
        for item in wishlist_query:
            success, msg = CartService.add_to_cart(user, item.product.id)
            if success:
                item.delete()
                items_moved += 1
        
        return items_moved

class DataMigrationService:
    @staticmethod
    def fix_slugs_and_categories():
        """Ensure all products have slugs and proper categories"""
        products = Product.objects.all()
        categories_created = 0
        slugs_fixed = 0
        
        for product in products:
            # Fix Slugs
            if not product.slug:
                product.slug = slugify(product.name)
                product.save()
                slugs_fixed += 1
            
            # Migrate Categories
            if product.category_old and not product.category:
                cat, created = Category.objects.get_or_create(name=product.category_old)
                product.category = cat
                product.save()
                if created: categories_created += 1
        
        return slugs_fixed, categories_created

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(user, address_data, cart_items, total_price, razorpay_data=None):
        """Standardized order creation logic"""
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            shipping_address=address_data.get('address'),
            shipping_city=address_data.get('city'),
            shipping_pincode=address_data.get('pincode'),
            razorpay_order_id=razorpay_data.get('id') if razorpay_data else ''
        )
        
        for item in cart_items:
            product = Product.objects.select_for_update().get(id=item['id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price_at_purchase=product.price
            )
            # Reduce stock
            product.stock -= item['quantity']
            product.save()
            
        return order
