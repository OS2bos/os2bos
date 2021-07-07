# Copyright (C) 2019 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


"""bevillingsplatform URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/

Examples
--------
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
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.views.generic import TemplateView
from watchman.views import status
import django_saml2_auth

from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core import views

router = routers.DefaultRouter()
router.register(r"cases", views.CaseViewSet)
router.register(r"appropriations", views.AppropriationViewSet, "appropriation")
router.register(r"activities", views.ActivityViewSet, "activity")
router.register(
    r"payment_schedules", views.PaymentScheduleViewSet, "paymentschedule"
)
router.register(r"rates", views.RateViewSet, "rate")
router.register(r"prices", views.PriceViewSet, "price")
router.register(r"payment_method_details", views.PaymentMethodDetailsViewSet)
router.register(r"payments", views.PaymentViewSet)
router.register(r"related_persons", views.RelatedPersonViewSet)
router.register(r"municipalities", views.MunicipalityViewSet)
router.register(r"school_districts", views.SchoolDistrictViewSet)
router.register(r"teams", views.TeamViewSet)
router.register(r"sections", views.SectionViewSet)
router.register(r"sectioninfos", views.SectionInfoViewSet)
router.register(r"activity_details", views.ActivityDetailsViewSet)
router.register(r"service_providers", views.ServiceProviderViewSet)
router.register(r"approval_levels", views.ApprovalLevelViewSet)
router.register(r"users", views.UserViewSet)
router.register(r"effort_steps", views.EffortStepViewSet)
router.register(r"target_groups", views.TargetGroupViewSet)
router.register(
    r"internal_payment_recipients", views.InternalPaymentRecipientViewSet
)
router.register(r"efforts", views.EffortViewSet)

urlpatterns = [
    # These are the SAML2 related URLs. You can change
    # "^saml2_auth/" regex to
    # any path you want, like "^sso_auth/", "^sso_login/", etc.
    # (required)
    url(r"^api/saml2_auth/", include("django_saml2_auth.urls")),
    # The following line will replace the default user login with
    # SAML2 (optional)
    # If you want to specific the after-login-redirect-URL, use
    # parameter "?next=/the/path/you/want"
    # with this view.
    url(r"^api/accounts/login/$", django_saml2_auth.views.signin),
    # The following line will replace the admin login with SAML2
    # (optional)
    # If you want to specific the after-login-redirect-URL, use
    # parameter "?next=/the/path/you/want"
    # with this view.
    url(r"^api/admin/login/$", django_saml2_auth.views.signin),
    # The following line will replace the default admin user logout with
    # the signout page (optional)
    url(r"^api/admin/logout/$", django_saml2_auth.views.signout),
    path("api/admin/", admin.site.urls),
    path("api/auth/", include("rest_framework.urls")),
    path(
        "api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/", include(router.urls)),
    path(
        "api/openapi/",
        get_schema_view(
            title="OS2bos REST API",
            description="API for accessing the OS2bos data model",
            # version="1.0.0",
        ),
        name="openapi-schema",
    ),
    path(
        "api/swagger-ui/",
        TemplateView.as_view(
            template_name="core/html/swagger-ui.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
    path(
        "api/frontend-settings/",
        views.FrontendSettingsView.as_view(),
        name="frontend-settings",
    ),
    path("api/healthcheck/", status),
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
        r"^(?P<path>(?:(?:js|css|img|fonts)\/.*|favicon.ico|logo.png))$",
        serve,
        kwargs={"document_root": _frontend_root},
    ),
    re_path(
        r"^(?:index.html)?$",
        serve,
        kwargs={"document_root": _frontend_root, "path": "index.html"},
    ),
]
