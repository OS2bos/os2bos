"""bevillingsplatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core import views

router = routers.DefaultRouter()
router.register(r"cases", views.CaseViewSet)
router.register(r"appropriations", views.AppropriationViewSet)
router.register(r"activities", views.ActivityViewSet)
router.register(r"payment_schedules", views.PaymentScheduleViewSet)
router.register(r"payment_method_details", views.PaymentMethodDetailsViewSet)
router.register(r"payments", views.PaymentViewSet)
router.register(r"related_persons", views.RelatedPersonViewSet)
router.register(r"municipalities", views.MunicipalityViewSet)
router.register(r"school_districts", views.SchoolDistrictViewSet)
router.register(r"teams", views.TeamViewSet)
router.register(r"sections", views.SectionViewSet)
router.register(r"activity_details", views.ActivityDetailsViewSet)
router.register(r"service_providers", views.ServiceProviderViewSet)
router.register(r"approval_levels", views.ApprovalLevelViewSet)
router.register(r"users", views.UserViewSet)
router.register(r"accounts", views.AccountViewSet)

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/auth/", include("rest_framework.urls")),
    path(
        "api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/", include(router.urls)),
]

# Static files are served by WhiteNoise in both development and production.
#
# We serve the static file at two URLs. The first is the one normal to Django
# where we serve everything in STATIC_ROOT at the STATIC_URL (default:
# `/api/static/`).

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# On the second one we serve everything in `STATIC_ROOT/frontend`. The vue
# frontend can be put here. It is served at the root of the URL, including
# `STATIC_ROOT/frontend/index.html` at the root.

_frontend_root = settings.STATIC_ROOT + "/frontend"
urlpatterns += [
    re_path(
        r"^(?P<path>(?:(?:js|css|img)\/.*|favicon.ico|logo.svg))$",
        serve,
        kwargs={"document_root": _frontend_root},
    ),
    re_path(
        r"^(?:index.html)?$",
        serve,
        kwargs={"document_root": _frontend_root, "path": "index.html"},
    ),
]
