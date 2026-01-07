from .models import Cart, Wishlist

def cart_wishlist_counts(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.item_count
        except Cart.DoesNotExist:
            cart_count = 0
            
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return {
            'cart_count': cart_count,
            'wishlist_count': wishlist_count
        }
    return {
        'cart_count': 0,
        'wishlist_count': 0
    }
