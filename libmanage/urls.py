from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication


schema_view = get_schema_view(
   openapi.Info(
      title="Library Management System API",
      default_version='v1',
      description="""
      API for Library Management System

      ## Authentication
      - Use `/register/` to register as a user
      - Use `/api/token/` to obtain JWT tokens after registering
      - Include token in header: `Authorization: Bearer <access_token>`, you can use extensions like Mobheader
      
      ## Endpoints
      - Authors CRUD
      - Books CRUD
      - Borrow and Return Books
      - Generate Library Reports
      """,
      contact=openapi.Contact(email="contact@librarymanage.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=(JWTAuthentication,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
