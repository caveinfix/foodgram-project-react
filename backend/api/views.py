from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (
    FollowAuthorSerializer,
    FavoriteRecipeSerializer,
    FollowsSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShopingRecipeSerializer,
    TagSerializer,
    UserSerializer,
)
from .utils import delete_method, post_method
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Shopping,
    Tag,
)
from users.models import Follow, User


class UserViewSet(UserViewSet):
    """Вьюсет для пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ("username", "email")
    pagination_class = PageNumberPagination
    permission_classes = (AllowAny,)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        if request.method == "POST":
            author = get_object_or_404(User, id=id)
            user = request.user
            serializer = FollowAuthorSerializer(
                data={"user": user.id, "author": author.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            follow = get_object_or_404(
                Follow,
                author=get_object_or_404(User, id=id),
                user=request.user,
            )
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["GET"], detail=False, permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = Follow.objects.filter(author__following__user=request.user)
        page_obj = self.paginate_queryset(queryset)
        serializer = FollowsSerializer(
            page_obj, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly,)
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
            return post_method(request, pk, FavoriteRecipeSerializer)
        elif request.method == "DELETE":
            return delete_method(request, pk, Favorite)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return post_method(request, pk, ShopingRecipeSerializer)
        elif request.method == "DELETE":
            return delete_method(request, pk, Shopping)

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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    "Вьюесет для ингредиентов."
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ("^name",)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
