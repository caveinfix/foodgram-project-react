from rest_framework import routers

from django.urls import include, path
# from django.conf import settings
from django.conf.urls.static import static

from .views import RecipeViewSet, IngredientViewSet, TagViewSet, UserViewSet


router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="recipes")
router.register(r"recipes", RecipeViewSet, basename="recipes")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"tags", TagViewSet, basename="tags")


urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
