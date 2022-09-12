from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from recipes.models import Recipe, Ingredient, IngredientRecipe, Tag, Favorite, Shopping
from users.models import Follow
import base64
from users.models import User
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import AnonymousUser

from rest_framework.validators import UniqueTogetherValidator


class Base64ImageField(serializers.ImageField):
    "Сериалайзер для картинок."

    def to_representation(self, value):
        return value.url

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для пользоателей."""

    is_subscribed = serializers.SerializerMethodField()
    # username = serializers.SlugField()

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
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.id).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    "Сериалайзер для подписки пользователей на автора."
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ("id", "user", "author")


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    # author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ("id", "user", "recipe")


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения сокращенного превью рецепта в подписке."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscribtionsSerializer(serializers.ModelSerializer):
    """Сериалайзер для отображения авторов с рецептами в подписке, на которых подписан пользователь."""

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
        """Получаем доступ к объекту запроса, а затем получить атрибут пользователя."""
        # Объект requestсодержит информацию о запросе пользователя. Какие данные они отправили на страницу, откуда они поступают и т. д.
        request = self.context.get("request")
        # #request.GETсодержит переменные GET. Это то, что вы видите в адресной строке вашего браузера. Этот .get()метод используется для словарей. Ваш фрагмент кода говорит: «Получите значение переменной GET с именем« страница http://localhost/api/users/subscriptions/?page=1&limit=6&recipes_limit=3 ».
        # Получим значение recipes_limit = 3
        recipes_limit = request.GET.get("recipes_limit")
        # Получим queryset всех рецептов автора [<recipe:name1>,<recipe:name2>,.....]
        queryset = Recipe.objects.filter(author=obj.author)
        # Если 3
        if recipes_limit:
            # Присвоим значению queryset первые 3 объекта
            queryset = queryset[: int(recipes_limit)]
            # Передадим наш queryset SubscriptionRecipeSerializer и он выведет только 3 объекта
        return SubscriptionRecipeSerializer(queryset, many=True).data

    @staticmethod
    def get_is_subscribed(obj):
        return Follow.objects.filter(user=obj.user, author=obj.author).exists()

    @staticmethod
    def get_recipes_count(obj):
        return Recipe.objects.filter(author=obj.author).count()


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


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиента."""

    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиента."""

    class Meta:
        model = Ingredient
        fields = "__all__"


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
    is_favorited = serializers.SerializerMethodField(
        method_name="get_is_favorited", read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart", read_only=True
    )

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
            "is_in_shopping_cart"
        )

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorite__user=user, id=obj.id).exists()


    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(shopping_cart__user=user, id=obj.id).exists()


    def validate(self, data):
        ingredients = self.initial_data.get("ingredients")
        tags = self.initial_data.get("tags")
        if not tags:
            raise serializers.ValidationError(
                {"tags": "Нужно выбрать хотя бы 1 тэг!"}
            )
        lst = []
        for ingredient in ingredients:
            obj_amount = int(ingredient.get("amount"))
            if obj_amount <= 0:
                raise serializers.ValidationError(
                    "Нужно добавить хотя бы один игридиент!"
                )
            obj_id = ingredient.get("id")
            if obj_id in lst:
                raise serializers.ValidationError(
                    "Ингридиент не должен повторяться!"
                )
            lst.append(obj_id)
        data["ingredients"] = ingredients
        data["tags"] = tags
        return data

    def create(self, validated_data):
        # Уберем список ингридиентов из словаря validated_data и сохраним его
        ingredients = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        image = validated_data.pop("image")
        # Создадим новый рецепт пока без ингридиентов
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags_data)
        for ingredient in ingredients:
            # Создадим связь с существующим экземпляром ингридиента и рецептом
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
        # Удаление или добавление нового тэга из экземляра
        tags = validated_data.pop("tags")
        instance.tags.clear()
        instance.tags.set(tags)
        # Удаление или добавление нового ингридиента из экземляра
        IngredientRecipe.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.pop("ingredients")
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get("id"),
                amount=ingredient.get("amount"),
            )
        instance.save()
        return instance



class ShopingRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shopping
        fields = ("id", "user", "recipe")


class ShopingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopping
        fields = ("id", "name", "image", "cooking_time")