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
    checkout
)

urlpatterns = [

    # USER / AUTH
    path(
        "register/",
        register_view,
        name="register"
    ),

    path(
        "login/",
        login_view,
        name="login"
    ),

    # CATEGORY
    path(
        "categories/",
        category_list,
        name="categories"
    ),

    # PRODUCT
    path(
        "products/",
        product_list,
        name="product_list"
    ),

    # CART
    path(
        "cart/",
        cart_list,
        name="cart_list"
    ),

    path(
        "cart/add/",
        add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/item/<int:item_id>/",
        cart_item_detail,
        name="cart_item_detail"
    ),

    path(
        "cart/<int:cart_id>/",
        cart_details,
        name="cart_details"
    ),

    path(
        "checkout/",
        checkout,
        name="checkout"
    ),
]