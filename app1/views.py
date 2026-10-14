from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
    AllowAny,
)
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db import IntegrityError

from .models import User, Category, Product, Cart, CartDetails, Rating, Coupon

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    CategorySerializer,
    ProductSerializer,
    CartSerializer,
    CartDetailsSerializer,
    RatingSerializer,
    RatingModerationSerializer,
    CouponSerializer,
)


# ============================================================
# HELPERS
# ============================================================

def user_has_purchased(user, product):
    # TODO: after we create Order and OrderItem models,
    # check here that this user really bought this product.
    # Until then everyone is allowed to review.
    return True


# ============================================================
# REGISTER
# ============================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    try:
        serializer = RegisterSerializer(data=request.data)

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
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
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


# ============================================================
# CHECKOUT
# ============================================================

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


# ============================================================
# REVIEWS: LIST + CREATE
# ============================================================

# GET  /products/<product_id>/reviews/   (anyone)
# POST /products/<product_id>/reviews/   (logged in)  body: {"score": 1-5, "comment": "..."}
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_reviews(request, product_id):

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # ---------- GET: show approved reviews ----------
    if request.method == "GET":

        reviews = (
            product.ratings
            .filter(status=Rating.Status.APPROVED)
            .select_related("user")
            .order_by("-created_at")
        )

        my_review = None
        if request.user.is_authenticated:
            mine = Rating.objects.filter(
                user=request.user,
                product=product
            ).first()
            if mine:
                my_review = RatingSerializer(mine).data

        return Response(
            {
                "average_rating": float(product.average_rating),
                "review_count": product.review_count,
                "my_review": my_review,
                "reviews": RatingSerializer(reviews, many=True).data,
            },
            status=status.HTTP_200_OK
        )

    # ---------- POST: add a review ----------
    if not user_has_purchased(request.user, product):
        return Response(
            {"error": "Only customers who bought this product can review it."},
            status=status.HTTP_403_FORBIDDEN
        )

    if Rating.objects.filter(user=request.user, product=product).exists():
        return Response(
            {"error": "You already reviewed this product. Edit your review instead."},
            status=status.HTTP_409_CONFLICT
        )

    serializer = RatingSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # user and product come from the server, never from the request body
        serializer.save(user=request.user, product=product)
    except IntegrityError:
        # two requests at the same moment: the database blocks the second one
        return Response(
            {"error": "You already reviewed this product."},
            status=status.HTTP_409_CONFLICT
        )

    return Response(
        {
            "message": "Review added.",
            "review": serializer.data,
        },
        status=status.HTTP_201_CREATED
    )


# ============================================================
# REVIEWS: EDIT / DELETE (owner or admin)
# ============================================================

# PATCH  /reviews/<review_id>/   body: {"score": 4, "comment": "..."}
# DELETE /reviews/<review_id>/
@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def review_detail(request, review_id):

    try:
        review = Rating.objects.select_related("user", "product").get(id=review_id)
    except Rating.DoesNotExist:
        return Response(
            {"error": "Review not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # ownership check: only the owner (or an admin) can change it
    if review.user_id != request.user.id and not request.user.is_staff:
        return Response(
            {"error": "You can only change your own review."},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == "DELETE":
        review.delete()
        return Response(
            {"message": "Review deleted."},
            status=status.HTTP_200_OK
        )

    serializer = RatingSerializer(
        review,
        data=request.data,
        partial=True
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save()

    return Response(
        {
            "message": "Review updated.",
            "review": serializer.data,
        },
        status=status.HTTP_200_OK
    )


# ============================================================
# QUICK RATE (old endpoint, kept so your frontend still works)
# ============================================================

# POST /products/<product_id>/rate/   body: {"score": 1-5, "comment": "optional"}
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_product(request, product_id):

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if not user_has_purchased(request.user, product):
        return Response(
            {"error": "Only customers who bought this product can review it."},
            status=status.HTTP_403_FORBIDDEN
        )

    existing = Rating.objects.filter(
        user=request.user,
        product=product
    ).first()

    # if the user already rated, update it. Otherwise create a new one.
    serializer = RatingSerializer(
        existing,
        data=request.data,
        partial=existing is not None
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        rating = serializer.save(user=request.user, product=product)
    except IntegrityError:
        return Response(
            {"error": "You already reviewed this product."},
            status=status.HTTP_409_CONFLICT
        )

    product.refresh_from_db()

    return Response(
        {
            "message": "Rating saved.",
            "my_rating": rating.score,
            "average_rating": float(product.average_rating),
            "rating_count": product.review_count,
        },
        status=status.HTTP_200_OK
    )


# ============================================================
# ADMIN MODERATION
# ============================================================

# GET /moderation/reviews/?status=pending|approved|hidden
@api_view(["GET"])
@permission_classes([IsAdminUser])
def moderation_review_list(request):

    reviews = (
        Rating.objects
        .select_related("user", "product")
        .order_by("-created_at")
    )

    status_filter = request.query_params.get("status")

    if status_filter:
        if status_filter not in Rating.Status.values:
            return Response(
                {"error": f"status must be one of {list(Rating.Status.values)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        reviews = reviews.filter(status=status_filter)

    return Response(
        RatingModerationSerializer(reviews, many=True).data,
        status=status.HTTP_200_OK
    )


# PATCH  /moderation/reviews/<review_id>/   body: {"status": "hidden"}
# DELETE /moderation/reviews/<review_id>/
@api_view(["PATCH", "DELETE"])
@permission_classes([IsAdminUser])
def moderation_review_detail(request, review_id):

    try:
        review = Rating.objects.select_related("user", "product").get(id=review_id)
    except Rating.DoesNotExist:
        return Response(
            {"error": "Review not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "DELETE":
        review.delete()
        return Response(
            {"message": "Review deleted by admin."},
            status=status.HTTP_200_OK
        )

    serializer = RatingModerationSerializer(
        review,
        data=request.data,
        partial=True
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save()

    return Response(
        {
            "message": "Review status updated.",
            "review": serializer.data,
        },
        status=status.HTTP_200_OK
    )


# ============================================================
# ADMIN: COUPON LIST + CREATE
# ============================================================

# GET  /manage/coupons/?active=true|false
# POST /manage/coupons/
@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def coupon_list(request):

    # ---------- GET: list all coupons ----------
    if request.method == "GET":

        coupons = Coupon.objects.all().order_by("-created_at")

        active = request.query_params.get("active")
        if active is not None:
            coupons = coupons.filter(is_active=active.lower() == "true")

        return Response(
            CouponSerializer(coupons, many=True).data,
            status=status.HTTP_200_OK
        )

    # ---------- POST: create a coupon ----------
    serializer = CouponSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save()

    return Response(
        {
            "message": "Coupon created.",
            "coupon": serializer.data,
        },
        status=status.HTTP_201_CREATED
    )


# ============================================================
# ADMIN: COUPON VIEW / EDIT / DELETE
# ============================================================

# GET    /manage/coupons/<coupon_id>/
# PATCH  /manage/coupons/<coupon_id>/
# DELETE /manage/coupons/<coupon_id>/
@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAdminUser])
def coupon_detail(request, coupon_id):

    try:
        coupon = Coupon.objects.get(id=coupon_id)
    except Coupon.DoesNotExist:
        return Response(
            {"error": "Coupon not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        return Response(
            CouponSerializer(coupon).data,
            status=status.HTTP_200_OK
        )

    if request.method == "DELETE":
        coupon.delete()
        return Response(
            {"message": "Coupon deleted."},
            status=status.HTTP_200_OK
        )

    # PATCH
    serializer = CouponSerializer(
        coupon,
        data=request.data,
        partial=True
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save()

    return Response(
        {
            "message": "Coupon updated.",
            "coupon": serializer.data,
        },
        status=status.HTTP_200_OK
    )