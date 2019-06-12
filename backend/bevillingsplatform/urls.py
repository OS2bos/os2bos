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
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers
from core import views

router = routers.DefaultRouter()
router.register(r"cases", views.CaseViewSet)
router.register(r"appropriations", views.AppropriationViewSet)
router.register(r"activities", views.ActivityViewSet)
router.register(r"payment_schedules", views.PaymentScheduleViewSet)
router.register(r"payments", views.PaymentViewSet)
router.register(r"related_persons", views.RelatedPersonViewSet)
router.register(r"municipalities", views.MunicipalityViewSet)
router.register(r"school_districts", views.SchoolDistrictViewSet)
router.register(r"sections", views.SectionsViewSet)
router.register(r"activity_catalogs", views.ActivityCatalogViewSet)
router.register(r"users", views.UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("rest_framework.urls")),
    path("", include(router.urls)),
] + static("/static/", document_root=settings.STATIC_ROOT)
