from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Category, Product, Cart, CartDetails, Rating, Coupon

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartDetails)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "quantity", "average_rating", "review_count")
    readonly_fields = ("average_rating", "review_count")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "score", "status", "created_at")
    list_filter = ("status", "score")
    search_fields = ("product__name", "user__username", "comment")
    actions = ["approve_reviews", "hide_reviews"]

    # We loop and call save() instead of queryset.update().
    # update() skips signals, so the product's average would NOT refresh.
    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        for rating in queryset:
            rating.status = Rating.Status.APPROVED
            rating.save()

    @admin.action(description="Hide selected reviews")
    def hide_reviews(self, request, queryset):
        for rating in queryset:
            rating.status = Rating.Status.HIDDEN
            rating.save()


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code", "discount_type", "discount_value", "min_order_value",
        "expiry_date", "used_count", "usage_limit", "is_active",
    )
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)
    readonly_fields = ("used_count",)