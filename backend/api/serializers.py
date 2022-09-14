import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from users.models import Follow, User
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    Shopping,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тегов."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиента."""

    class Meta:
        model = Ingredient
        fields = "__all__"


class Base64ImageField(serializers.ImageField):
    "Сериалайзер для картинок."

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для пользоателей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class ChangePasswordSerializer(serializers.ModelSerializer):
    """Сериалайзер для смена пароля."""

    new_password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "new_password",
            "current_password",
        )


class FollowsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для подробного отображения автора с
    рецептами в подписке, на которых подписан
    пользователь.
    """

    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        queryset = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[: int(recipes_limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class FallowAuthorSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления в подписчики."""

    class Meta:
        model = Follow
        fields = ("id", "user", "author")

    def validate(self, data):
        author = self.initial_data.get("author")
        user = self.context.get("request").user
        if author == user:
            raise serializers.ValidationError("Нельзя подписаться на себя!")
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError("Вы уже подписаны!")
        return data

    def to_representation(self, instance):
        serializer = FollowsSerializer(instance, context=self.context)
        return serializer.data


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""

    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        source="ingredient_recipe",
        many=True,
        read_only=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "name",
            "text",
            "cooking_time",
            "image",
            "tags",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Shopping.objects.filter(user=user, recipe=obj).exists()

    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        tags = self.initial_data.get("tags")
        if not tags:
            raise serializers.ValidationError("Нужно выбрать тег!")
        if not ingredients:
            raise serializers.ValidationError("Добавьте ингридиенты!")
        lst = []
        for ingredient in ingredients:
            ingredient = ingredient.get("id")
            if ingredient in lst:
                raise serializers.ValidationError("Ингридиент уже добавлен!")
            lst.append(ingredient)
        data["ingredients"] = ingredients
        data["tags"] = tags
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.image = validated_data.get("image", instance.image)
        tags = validated_data.pop("tags")
        instance.tags.clear()
        instance.tags.set(tags)
        ingredients = validated_data.pop("ingredients")
        IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )
        instance.save()
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения сокращенного превью."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления в избранное."""

    class Meta:
        model = Favorite
        fields = ("id", "user", "recipe")

    def validate(self, data):
        request = self.context.get("request")
        recipe_id = data["recipe"].id
        if Favorite.objects.filter(
            user=request.user, recipe__id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                "Рецепт уже добавлен в избранное!"
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return ShortRecipeSerializer(instance.recipe, context=context).data


class ShopingRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления в список покупок."""

    class Meta:
        model = Shopping
        fields = ("id", "user", "recipe")

    def validate(self, data):
        request = self.context.get("request")
        recipe_id = data["recipe"].id
        if Shopping.objects.filter(
            user=request.user, recipe__id=recipe_id
        ).exists():
            raise serializers.ValidationError(
                "Рецепт уже добавлен в список покупок!"
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return ShortRecipeSerializer(instance.recipe, context=context).data
