from django.contrib import admin
from .models import Product, ProductImage, Order, OrderItem, Category, Cart, CartItem, Review, Coupon
from import_export.admin import ImportExportModelAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('name', 'price', 'stock', 'get_category', 'slug', 'is_featured')
    list_filter = ('category_obj', 'is_featured', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

    def get_category(self, obj):
        return obj.category_obj.name if obj.category_obj else "None"
    get_category.short_description = 'Category'

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active', 'expires_at')
    list_filter = ('is_active',)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Review)
