from django.urls import path

from .views import (
    register_view,
    login_view, 
)


urlpatterns = [
    path("api/register/", register_view, name="register"),

    path("api/login/", login_view,name="login" ),
    # path("categories/", category_list, name="category-list"),
    # path("categories/<int:id>/", category_detail, name="category-detail"),
    # path("profile/", profile_view, name="profile"),


    # path("products/",product_list,name="product-list"),

    # path("products/<int:id>/", product_detail, name="product-detail")

]