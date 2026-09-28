from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .models import User, Category, Product, Cart, CartDetails

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    CartDetailsSerializer
)


# ============================================================
# REGISTER
# ============================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):

    serializer = RegisterSerializer(
        data=request.data
    )

    if serializer.is_valid():
        user = serializer.save()

        return Response(
            {
                "message": "Registration successful.",
                "user": RegisterSerializer(user).data,
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ============================================================
# LOGIN
# ============================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):

    serializer = LoginSerializer(
        data=request.data
    )

    if serializer.is_valid():
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ============================================================
# CATEGORY
# ============================================================

# GET /categories/
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def category_list(request):

    # GET /categories/
    if request.method == "GET":

        categories = Category.objects.all()

        serializer = CategorySerializer(
            categories,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # POST /categories/
    serializer = CategorySerializer(
        data=request.data
    )

    if serializer.is_valid():
        serializer.save()

        return Response(
            {
                "message": "Category added successfully.",
                "category": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ============================================================
# PRODUCT
# ============================================================

# GET /products/
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def product_list(request):

    # GET /products/
    if request.method == "GET":

        products = Product.objects.all()

        serializer = ProductSerializer(
            products,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # POST /products/
    serializer = ProductSerializer(
        data=request.data
    )

    if serializer.is_valid():
        serializer.save()

        return Response(
            {
                "message": "Product added successfully.",
                "product": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# ============================================================
# CART
# ============================================================

# GET /cart/
# POST /cart/
@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def cart_list(request):

    # GET /cart/
    if request.method == "GET":

        carts = Cart.objects.all()

        serializer = CartSerializer(
            carts,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # POST /cart/
    user_id = request.data.get("user")

    if not user_id:
        return Response(
            {"error": "User ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if Cart.objects.filter(user_id=user_id).exists():

        return Response(
            {"error": "Cart already exists for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )

    cart = Cart.objects.create(
        user_id=user_id
    )

    serializer = CartSerializer(cart)

    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )


# ============================================================
# ADD PRODUCT TO CART
# ============================================================

# POST /cart/add/
@api_view(["POST"])
@permission_classes([AllowAny])
def add_to_cart(request):

    cart_id = request.data.get("cart")
    product_id = request.data.get("product")
    quantity = request.data.get("quantity")

    # Check cart ID
    if not cart_id:

        return Response(
            {"error": "Cart ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check product ID
    if not product_id:

        return Response(
            {"error": "Product ID is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check quantity
    if not quantity:

        return Response(
            {"error": "Quantity is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Find product
    try:

        product = Product.objects.get(
            id=product_id
        )

    except Product.DoesNotExist:

        return Response(
            {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Find cart
    try:

        cart = Cart.objects.get(
            id=cart_id
        )

    except Cart.DoesNotExist:

        return Response(
            {"error": "Cart not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check whether product already exists in cart
    cart_detail = CartDetails.objects.filter(
        cart=cart,
        product=product
    ).first()

    if cart_detail:

        # Increase existing quantity
        cart_detail.quantity += int(quantity)

        cart_detail.save()

    else:

        # Add new product to cart
        cart_detail = CartDetails.objects.create(
            cart=cart,
            product=product,
            price_per=product.price,
            quantity=quantity
        )

    serializer = CartDetailsSerializer(
        cart_detail
    )

    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
    )


# ============================================================
# UPDATE / DELETE A CART DETAIL ITEM
# ============================================================

# PATCH /cart/item/<item_id>/  — change quantity
# DELETE /cart/item/<item_id>/ — remove item
@api_view(["PATCH", "DELETE"])
@permission_classes([AllowAny])
def cart_item_detail(request, item_id):

    try:
        item = CartDetails.objects.get(id=item_id)
    except CartDetails.DoesNotExist:
        return Response(
            {"error": "Cart item not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # DELETE — remove the item entirely
    if request.method == "DELETE":
        item.delete()
        return Response(
            {"message": "Item removed from cart"},
            status=status.HTTP_200_OK
        )

    # PATCH — update quantity
    quantity = request.data.get("quantity")

    if quantity is None:
        return Response(
            {"error": "quantity is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    quantity = int(quantity)

    if quantity <= 0:
        # treat quantity 0 or negative as a remove
        item.delete()
        return Response(
            {"message": "Item removed from cart"},
            status=status.HTTP_200_OK
        )

    item.quantity = quantity
    item.save()

    serializer = CartDetailsSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================
# VIEW ONE CART
# ============================================================

# GET /cart/<cart_id>/
@api_view(["GET"])
@permission_classes([AllowAny])
def cart_details(request, cart_id):

    try:

        cart = Cart.objects.get(
            id=cart_id
        )

    except Cart.DoesNotExist:

        return Response(
            {"error": "Cart not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CartSerializer(
        cart
    )

    data = serializer.data

    # Calculate complete cart total
    total = 0

    for item in cart.cart_details.all():

        total += item.total_amount

    data["cart_total"] = total

    return Response(
        data,
        status=status.HTTP_200_OK
    )
# ------------------------------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user

    try:
        html_content = render_to_string(
            "Email/checkout.html",
            {
                "user": user,
            }
        )

        text_content = f"""
        Hello {user.first_name or user.username},

        Your order has been successfully placed.

        Thank you for shopping with us.
        """

        email = EmailMultiAlternatives(
            subject="Order Successfully Placed",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(
            html_content,
            "text/html"
        )

        email.send(
            fail_silently=False
        )

        return Response({
            "message": "Order successfully placed! Email sent successfully."
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )