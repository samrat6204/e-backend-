from django.urls import path

from .views import (
    register_view,
    login_view,
    category_list,
    product_list,
    cart_list,
    add_to_cart,
    cart_item_detail,
    cart_details,
    checkout,
    rate_product,
    product_reviews,
    review_detail,
    moderation_review_list,
    moderation_review_detail,
    coupon_list,
    coupon_detail,
    place_order,
    my_orders,
    order_detail,
)

urlpatterns = [

    # USER / AUTH
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),

    # CATEGORY
    path("categories/", category_list, name="categories"),

    # PRODUCT
    path("products/", product_list, name="product_list"),

    # PRODUCT RATING (old quick-rate endpoint)
    path("products/<int:product_id>/rate/", rate_product, name="rate_product"),

    # REVIEWS
    path("products/<int:product_id>/reviews/", product_reviews, name="product_reviews"),
    path("reviews/<int:review_id>/", review_detail, name="review_detail"),

    # ADMIN MODERATION
    path("moderation/reviews/", moderation_review_list, name="moderation_review_list"),
    path("moderation/reviews/<int:review_id>/", moderation_review_detail, name="moderation_review_detail"),

    # ADMIN COUPONS
    path("manage/coupons/", coupon_list, name="coupon_list"),
    path("manage/coupons/<int:coupon_id>/", coupon_detail, name="coupon_detail"),

    # CART
    path("cart/", cart_list, name="cart_list"),
    path("cart/add/", add_to_cart, name="add_to_cart"),
    path("cart/item/<int:item_id>/", cart_item_detail, name="cart_item_detail"),
    path("cart/<int:cart_id>/", cart_details, name="cart_details"),

    # CHECKOUT (OLD - kept, only sends the email)
    path("checkout/", checkout, name="checkout"),

    # ORDERS (NEW - payment & checkout revision)
    path("orders/place/", place_order, name="place_order"),
    path("orders/", my_orders, name="my_orders"),
    path("orders/<int:order_id>/", order_detail, name="order_detail"),
]