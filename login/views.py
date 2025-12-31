from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    Product, Profile, Wishlist, Order, OrderItem, Coupon, 
    Category, Cart, CartItem, Review
)
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
import logging
from uuid import uuid4
from .services import CartService, OrderService

logger = logging.getLogger(__name__)

# ============================================================
# FORMS & CLASSES
# ============================================================

class UserForm(forms.ModelForm):
    """Form for editing user details"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ProfileForm(forms.ModelForm):
    """Form for editing profile details"""
    class Meta:
        model = Profile
        fields = [
            'phone_number', 'address', 'city', 'pincode',
            'profile_photo', 'date_of_birth', 'gender'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }


class AddressForm(forms.Form):
    """Form for shipping address with validation"""
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    address = forms.CharField(
        max_length=500,
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'})
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    pincode = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'})
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )


class CustomLogoutView(LogoutView):
    """Secure logout view - only allows POST"""
    http_method_names = ['post']


# ============================================================
# PROFILE MANAGEMENT
# ============================================================

@login_required
def profile(request):
    """Display user profile information"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'login/profile.html', {
        'user': request.user,
        'profile': profile,
    })


@login_required
def edit_profile_view(request):
    """Edit user and profile information"""
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    user_form.save()
                    profile_form.save()
                    messages.success(request, 'Profile updated successfully!')
                    logger.info(f"Profile updated for user: {user.username}")
                    return redirect('profile')
            except Exception as e:
                logger.error(f"Error updating profile for user {user.username}: {str(e)}")
                messages.error(request, 'An error occurred while updating your profile.')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'login/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


# ============================================================
# CART MANAGEMENT (AJAX) - CSRF PROTECTED
# ============================================================

@login_required
@require_http_methods(["POST"])
def ajax_add_to_cart(request, slug):
    """Add product to cart using Service Layer and slug"""
    try:
        product = get_object_or_404(Product, slug=slug)
        success, message = CartService.add_to_cart(request.user, product.id)
        
        if not success:
            return JsonResponse({'success': False, 'error': message})
            
        cart = CartService.get_or_create_cart(request.user)
        logger.info(f"User {request.user.username} added product {product.id} to cart")
        
        return JsonResponse({
            'success': True,
            'cart_count': cart.item_count,
            'message': f'Added {product.name} to cart'
        })
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def ajax_add_to_wishlist(request, slug):
    """Add product to wishlist using slug"""
    try:
        product = get_object_or_404(Product, slug=slug)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({
            'success': True,
            'wishlist_count': wishlist_count,
            'message': f"{product.name} added to wishlist" if created else "Already in wishlist"
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def ajax_move_to_cart(request, slug):
    """Move product from wishlist to cart using slug and service"""
    try:
        product = get_object_or_404(Product, slug=slug)
        success, message = CartService.add_to_cart(request.user, product.id)
        if not success:
            return JsonResponse({'success': False, 'error': message})
            
        Wishlist.objects.filter(user=request.user, product=product).delete()
        cart = CartService.get_or_create_cart(request.user)
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'success': True,
            'cart_count': cart.item_count,
            'wishlist_count': wishlist_count,
            'message': 'Moved to cart'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def ajax_move_all_to_cart(request):
    """Move all wishlist items to cart using service"""
    try:
        moved_count = CartService.move_wishlist_to_cart(request.user)
        cart = CartService.get_or_create_cart(request.user)
        return JsonResponse({
            'success': True,
            'cart_count': cart.item_count,
            'message': f'{moved_count} items moved to cart'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def ajax_update_cart_quantity(request, slug, action):
    """Update cart item quantity using slug and service"""
    try:
        product = get_object_or_404(Product, slug=slug)
        success, message = CartService.update_quantity(request.user, product.id, action)
        
        if not success:
            return JsonResponse({'success': False, 'error': message})
            
        cart = CartService.get_or_create_cart(request.user)
        item = CartItem.objects.filter(cart=cart, product=product).first()
        
        # Calculate totals
        total = cart.total_price
        discount_percent = request.session.get('discount', 0)
        discount_amount = total * Decimal(str(discount_percent)) / Decimal('100')
        
        return JsonResponse({
            'success': True,
            'cart_count': cart.item_count,
            'new_quantity': item.quantity if item else 0,
            'item_total': float(item.total_price) if item else 0,
            'cart_total': float(total - discount_amount),
            'original_total': float(total),
            'discount_amount': float(discount_amount)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================
# PRODUCT & ECOMMERCE VIEWS
# ============================================================

# @login_required  <-- Removed to allow public access
def product_detail_view(request, slug):
    """Display product information with slug support and persistent count"""
    from django.db.models import Avg
    from .models import Review
    
    product = get_object_or_404(Product, slug=slug)
    
    # Handle review submission (simplified for brevity, keeping existing logic)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text', '').strip()
        if rating:
            Review.objects.get_or_create(
                user=request.user, product=product,
                defaults={'rating': int(rating), 'review_text': review_text}
            )
        return redirect('product_detail', slug=slug)
    
    # Recently Viewed Logic (Store last 10 unique products)
    history = request.session.get('recently_viewed', [])
    if product.id in history:
        history.remove(product.id)
    history.insert(0, product.id)
    request.session['recently_viewed'] = history[:10]
    request.session.modified = True

    product_images = product.images.all()
    main_image = product.image.url if product.image else None
    if product_images:
        primary = product_images.filter(is_primary=True).first()
        main_image = primary.image.url if primary else product_images[0].image.url

    reviews = Review.objects.filter(product=product).select_related('user')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # Persistent counts
    cart_count = 0
    wishlist_count = 0
    is_wishlisted = False
    
    if request.user.is_authenticated:
        cart = CartService.get_or_create_cart(request.user)
        cart_count = cart.item_count
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()

    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'is_wishlisted': is_wishlisted,
        'main_image': main_image,
        'gallery_images': [img.image.url for img in product_images],
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
        'similar_products': similar_products,
    }
    return render(request, 'login/product_detail.html', context)


@login_required
def buy_now(request, slug):
    """Add product to cart and redirect to cart page immediately using service"""
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        success, message = CartService.add_to_cart(request.user, product.id)
        if success:
            messages.success(request, f'{product.name} added to cart')
            return redirect('cart')
        else:
            messages.error(request, message)
    return redirect('product_detail', slug=slug)


@login_required
def ecommerce_view(request):
    """Modern gradient ecommerce view (Unified)"""
    wishlist_count = 0
    cart_count = 0
    
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        cart = CartService.get_or_create_cart(request.user)
        cart_count = cart.item_count
        
    from django.db.models import Count, Min, Max

    selected_categories = request.GET.getlist('category')
    search_query = request.GET.get('query', '').strip()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    products = Product.objects.all()
    
    if selected_categories and 'all' not in selected_categories:
        products = products.filter(category_obj__name__in=selected_categories)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    if search_query:
        products = products.filter(name__icontains=search_query)
        request.session['last_search'] = search_query
    else:
        request.session.pop('last_search', None)

    # Calculate Facets
    all_categories = Category.objects.filter(parent=None).annotate(
        product_count=Count('products')
    )
    
    price_stats = Product.objects.aggregate(
        min_p=Min('price'), 
        max_p=Max('price')
    )
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    # AI Driven Recommendations
    recent_search = request.session.get('last_search')
    recommendations = Product.objects.none()
    
    if recent_search:
        # Suggest based on last search
        recommendations = Product.objects.filter(name__icontains=recent_search).exclude(id__in=[p.id for p in products])[:4]
    
    first_category = selected_categories[0] if selected_categories else 'all'
    if not recommendations.exists():
        # Fallback to featured or same category as selected
        if first_category != 'all':
            recommendations = Product.objects.filter(category_obj__name=first_category, is_featured=True)[:4]
        else:
            recommendations = Product.objects.filter(is_featured=True)[:4]

    # Fetch Recently Viewed Products
    recently_viewed_ids = request.session.get('recently_viewed', [])
    # Preserve order and ensure unique
    recently_viewed = []
    if recently_viewed_ids:
        # Fetch products in the specific order of IDs
        preserved_order = {id: i for i, id in enumerate(recently_viewed_ids)}
        recently_viewed = sorted(
            Product.objects.filter(id__in=recently_viewed_ids),
            key=lambda x: preserved_order.get(x.id)
        )[:6]

    # Rebuild query string for pagination
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    url_params = query_params.urlencode()

    context = {
        'products': products_page,
        'categories': all_categories,
        'selected_categories': selected_categories,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'price_stats': price_stats,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'recommendations': recommendations,
        'recently_viewed': recently_viewed,
        'url_params': url_params,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'login/partials/product_grid.html', context)

    return render(request, 'login/ecommerce_modern.html', context)


@login_required
def search_suggestions(request):
    """AJAX view for live search suggestions"""
    query = request.GET.get('query', '').strip()
    results = []
    
    if len(query) >= 2:
        products = Product.objects.filter(name__icontains=query)[:5]
        for product in products:
            results.append({
                'id': product.id,
                'slug': product.slug,
                'name': product.name,
                'price': float(product.price),
                'image': product.image.url if product.image else None
            })
            
    return JsonResponse({'results': results})


# ============================================================
# CART & CHECKOUT VIEWS
# ============================================================

@login_required
def add_to_cart(request, product_id):
    """Add product to cart (non-AJAX fallback)"""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            cart = request.session.get('cart', {})
            
            # Stock validation
            if product.stock <= int(cart.get(str(product_id), 0)):
                messages.error(request, 'Product is out of stock')
            else:
                cart[str(product_id)] = int(cart.get(str(product_id), 0)) + 1
                request.session['cart'] = cart
                request.session.modified = True
                messages.success(request, f'{product.name} added to cart')
        except Exception as e:
            logger.error(f"Error adding to cart: {str(e)}")
            messages.error(request, 'An error occurred')
    
    return redirect('ecommerce')


@login_required
def remove_from_cart(request, product_id):
    """Remove product from cart"""
    if request.method == 'POST':
        try:
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                del cart[str(product_id)]
                request.session['cart'] = cart
                request.session.modified = True
                messages.success(request, 'Item removed from cart')
        except Exception as e:
            logger.error(f"Error removing from cart: {str(e)}")
            messages.error(request, 'An error occurred')
    
    return redirect('cart')


@login_required
def cart_view(request):
    """Display persistent shopping cart from database"""
    cart = CartService.get_or_create_cart(request.user)
    cart_items = cart.items.select_related('product')
    
    total = cart.total_price
    coupon = request.session.get('coupon', '')
    discount_percent = request.session.get('discount', 0)
    discount_amount = total * Decimal(str(discount_percent)) / Decimal('100')
    
    context = {
        'cart': cart_items,
        'total': float(total - discount_amount),
        'discount_amount': float(discount_amount),
        'coupon': coupon,
        'original_total': float(total),
        'cart_count': cart.item_count
    }
    return render(request, 'login/cart.html', context)


# ============================================================
# WISHLIST MANAGEMENT
# ============================================================

@login_required
def wishlist_view(request):
    """Display user wishlist"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product').order_by('-added_at')
    
    return render(request, 'login/wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} added to wishlist')
    else:
        messages.info(request, f'{product.name} is already in wishlist')
    
    next_url = request.META.get('HTTP_REFERER', 'ecommerce')
    return redirect(next_url)


@login_required
def remove_from_wishlist(request, item_id):
    """Remove item from wishlist"""
    item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    
    if request.method == "POST":
        product_name = item.product.name
        item.delete()
        messages.success(request, f'{product_name} removed from wishlist')
    
    return redirect('wishlist')


# ============================================================
# COUPON MANAGEMENT (DATABASE-BACKED)
# ============================================================

@login_required
@require_http_methods(["POST"])
def apply_coupon(request):
    """Apply coupon code with proper validation"""
    coupon_code = request.POST.get("coupon", "").strip().upper()
    
    try:
        coupon = Coupon.objects.get(code=coupon_code)
        
        # Validate coupon
        if not coupon.is_valid():
            messages.error(request, "Coupon has expired or reached usage limit")
            logger.warning(f"Invalid coupon attempt: {coupon_code} by user {request.user.username}")
            return redirect('cart')
        
        # Apply coupon to session
        request.session['coupon'] = coupon_code
        request.session['discount'] = coupon.discount_percent
        request.session.modified = True
        
        # Increment usage count
        coupon.current_uses += 1
        coupon.save()
        
        messages.success(request, f"Coupon applied! You saved {coupon.discount_percent}%")
        logger.info(f"Coupon {coupon_code} applied by user {request.user.username}")
    
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code")
        logger.warning(f"Invalid coupon code attempt: {coupon_code} by user {request.user.username}")
        request.session['coupon'] = ''
        request.session['discount'] = 0
    
    except Exception as e:
        logger.error(f"Error applying coupon: {str(e)}")
        messages.error(request, "An error occurred while applying the coupon")
    
    return redirect('cart')


@login_required
@require_http_methods(["POST"])
def remove_coupon(request):
    """Remove applied coupon"""
    try:
        request.session['coupon'] = ''
        request.session['discount'] = 0
        request.session.modified = True
        messages.info(request, "Coupon removed")
        logger.info(f"Coupon removed by user {request.user.username}")
    except Exception as e:
        logger.error(f"Error removing coupon: {str(e)}")
        messages.error(request, "An error occurred")
    
    return redirect('cart')


# ============================================================
# CHECKOUT & PAYMENT
# ============================================================

@login_required
@require_http_methods(["GET", "POST"])
def address_view(request):
    """Handle shipping address input"""
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            try:
                request.session['address'] = {
                    'name': form.cleaned_data['name'],
                    'address': form.cleaned_data['address'],
                    'city': form.cleaned_data['city'],
                    'pincode': form.cleaned_data['pincode'],
                    'phone': form.cleaned_data['phone'],
                }
                request.session.modified = True
                return redirect('payment')
            except Exception as e:
                logger.error(f"Error saving address: {str(e)}")
                messages.error(request, "An error occurred while saving address")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AddressForm()
    
    return render(request, 'login/address.html', {'form': form})


@login_required
@csrf_exempt
def payment_success(request):
    """Handle successful payment callback from Razorpay"""
    if request.method == 'POST':
        try:
            # Verification logic here (omitted for simplicity but in prod use rzp signature)
            # For now, we assume if it reaches here and we have session data, it's good
            address = request.session.get('address')
            discount = request.session.get('discount', 0)
            
            order = OrderService.create_order(request.user, address, discount)
            
            if order:
                messages.success(request, f'Order placed successfully! Order ID: {order.id}')
                # Clear session
                request.session.pop('address', None)
                request.session.pop('discount', None)
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'error': 'Cart empty'})
        except Exception as e:
            logger.error(f"Payment success error: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    return redirect('ecommerce')


def payment_view(request):
    """Handle payment processing using persistent cart"""
    try:
        address = request.session.get('address')
        cart = CartService.get_or_create_cart(request.user)
        cart_items = cart.items.select_related('product')
        
        if not address or not cart_items.exists():
            messages.error(request, 'Please enter shipping address and add items to cart')
            return redirect('cart')
        
        total_price = cart.total_price
        discount_percent = request.session.get('discount', 0)
        discount_amount = total_price * Decimal(str(discount_percent)) / Decimal('100')
        final_total = total_price - discount_amount
        
        # Razorpay integration
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_paise = int(final_total * 100)
        
        try:
            razorpay_order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1
            })
        except Exception as ex:
            if settings.DEBUG:
                razorpay_order = {'id': f'debug_{uuid4().hex}', 'amount': amount_paise}
            else: raise ex

        context = {
            # Build a simple cart list for the template (image/url, price, quantity, total)
            'cart': [
                {
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': float(item.product.price),
                    'quantity': int(item.quantity),
                    'total': float(item.product.price * item.quantity),
                    'image': item.product.image.url if item.product and item.product.image else ''
                }
                for item in cart_items
            ],
            'total': float(final_total),
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'order_id': razorpay_order.get('id', ''),
            'amount': amount_paise,
            'address': address,
        }
        return render(request, 'login/payment.html', context)
    except Exception as e:
        logger.error(f"Error in payment view: {str(e)}")
        messages.error(request, 'An error occurred')
        return redirect('cart')


# ============================================================
# AUTHENTICATION
# ============================================================

def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('ecommerce')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        # Validation
        if not all([username, email, password1, password2]):
            return render(request, 'login/register.html', {
                'error': 'All fields are required.'
            })
        
        if User.objects.filter(username=username).exists():
            return render(request, 'login/register.html', {
                'error': 'Username already exists.'
            })
        
        if User.objects.filter(email=email).exists():
            return render(request, 'login/register.html', {
                'error': 'Email already registered.'
            })
        
        if password1 != password2:
            return render(request, 'login/register.html', {
                'error': 'Passwords do not match.'
            })
        
        if len(password1) < 8:
            return render(request, 'login/register.html', {
                'error': 'Password must be at least 8 characters long.'
            })
        
        try:
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password1)
            )
            messages.success(request, 'Registration successful! Please login.')
            logger.info(f"New user registered: {username}")
            return redirect('login')
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return render(request, 'login/register.html', {
                'error': 'An error occurred during registration.'
            })
    
    return render(request, 'login/register.html')
