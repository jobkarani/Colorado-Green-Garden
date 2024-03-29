from django.contrib import admin
from .models import *

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','slug')
    prepopulated_fields = {'slug': ('name',)}

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'new_price', 'old_price','category', 'is_available')
    prepopulated_fields = {'slug': ('name',)}

class CartAdmin(admin.ModelAdmin):
    list_display = ('user','cart_id', 'date_added')
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'user', 'is_active')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','firstname','lastname','phone')

admin.site.register(Profile,ProfileAdmin)
admin.site.register(Product, ProductAdmin )
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ReviewRating)
