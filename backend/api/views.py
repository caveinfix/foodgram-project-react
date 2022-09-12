from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            Shopping, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShopingRecipeSerializer,
                          SubscribeSerializer, SubscribtionsSerializer,
                          TagSerializer, UserSerializer)


class UserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ("username", "email")
    permission_classes = (AllowAny,)

    @action(methods=["post", "delete"], detail=True)
    def subscribe(self, request, id):
        if request.method == "DELETE":
            follower = get_object_or_404(
                Follow,  # Переименовать в Subdcribe
                author=get_object_or_404(User, id=id),
                user=request.user,
            )
            follower.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == "POST":
            author = get_object_or_404(User, id=id)
            user = request.user
            serializer = SubscribeSerializer(
                data={"user": user.id, "author": author.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["get"], detail=False, permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = Follow.objects.filter(author__following__user=request.user)
        page_obj = self.paginate_queryset(queryset)
        serializer = SubscribtionsSerializer(
            page_obj, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            user = request.user
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = FavoriteRecipeSerializer(
                data={"user": user.id, "recipe": recipe.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            favorite = get_object_or_404(
                Favorite,
                recipe=get_object_or_404(Recipe, pk=pk),
                user=request.user,
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            user = request.user
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = ShopingRecipeSerializer(
                data={"user": user.id, "recipe": recipe.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            favorite = get_object_or_404(
                Shopping,
                recipe=get_object_or_404(Recipe, pk=pk),
                user=request.user,
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["GET"], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            IngredientRecipe.objects.filter(recipe__shopping_cart__user=user)
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(value=Sum("amount"))
            .order_by("ingredient__name")
        )
        response = HttpResponse(
            charset="utf-8",
            content_type="text/plain",
        )
        for ingredient in ingredients:
            output = f"""
            {ingredient["ingredient__name"]} - {
                ingredient["value"]} {
                    ingredient["ingredient__measurement_unit"]}
            """
            response.write(output)

        return response


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
