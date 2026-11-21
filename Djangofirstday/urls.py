"""
Saauzi — Root URL Configuration
================================
All requests come here first.

URL structure:
  /admin/          → Django admin panel
  /api/<path>      → All app1 API endpoints (with /api/ prefix)
  /<path>          → Same app1 endpoints (without prefix, for React pages)
  /media/<file>    → Uploaded product images served in development

Authentication:
  - Public endpoints  : No token required (register, login, GET products/categories)
  - Protected endpoints: Require  →  Authorization: Bearer <access_token>
  - Admin endpoints   : Require   →  is_staff = True on the user account
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # ── Django Admin Panel ───────────────────────────────────────────────────
    # Access at /admin/ — login with a superuser account.
    # Create superuser: py manage.py createsuperuser
    path("admin/", admin.site.urls),

    # ── API Routes (with /api/ prefix) ───────────────────────────────────────
    # Example: POST /api/login/   GET /api/products/
    # Used by the React app for auth endpoints (login, register).
    path("api/", include("app1.urls")),

    # ── API Routes (without prefix) ──────────────────────────────────────────
    # Example: GET /products/   POST /cart/add/
    # Used by React pages for products, categories, cart, orders.
    path("", include("app1.urls")),

# ── Media Files (development only) ───────────────────────────────────────────
# Serves uploaded product images at /media/<filename> during development.
# In production, serve media files via Nginx or a CDN instead.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
