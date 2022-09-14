from django.db import models
from users.models import User
from django.core.validators import MinValueValidator


class Tag(models.Model):
    "Модель тэгов."
    name = models.CharField("Тег", max_length=16, unique=True)
    color = models.CharField("Цвет HEX", max_length=8, unique=True)
    slug = models.SlugField("Slug", unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    "Модель ингридиентов."
    name = models.CharField("Название ингридиента", max_length=40)
    measurement_unit = models.CharField("Единица измерения", max_length=16)

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    "Модель рецепта."
    author = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        related_name="recipes",
        verbose_name="Инридиент",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги",
    )
    name = models.CharField("Название рецепиа", max_length=50)
    text = models.TextField("Описание рецепта")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=[
            MinValueValidator(1, message="Значение не может быть меньше 1."),
        ],
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        verbose_name="Изоображение",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    "Модель для указания количества ингридиента в рецепте."
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
        verbose_name="Ингридиент",
    )
    amount = models.PositiveIntegerField(
        "Количество",
        validators=[
            MinValueValidator(1, message="Значение не может быть меньше 1."),
        ],
    )

    class Meta:
        verbose_name = "Инридиент в рецепте"
        verbose_name_plural = "Инридиенты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="unique_ingredients"
            )
        ]

    def __str__(self):
        return f"В рецепт «{self.recipe}» добавлен {self.ingredient}"


class Favorite(models.Model):
    "Модель для избранных рецептов."
    user = models.ForeignKey(
        User,
        related_name="favorite",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="favorite",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Добавлен в избранное"
        verbose_name_plural = "Добавлены в избранное"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorites"
            )
        ]

    def __str__(self):
        return f"Рецепт «{self.recipe}» в избранном у пользователя {self.user}"


class Shopping(models.Model):
    "Модель для списка покупок."
    user = models.ForeignKey(
        User,
        related_name="shopping_cart",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="shopping_cart",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Добавлен в список покупок"
        verbose_name_plural = "Добавлены в список покупок"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shopping"
            )
        ]

    def __str__(self):
        return f""" Рецепт «{self.recipe}» добавлен
        в список покупок {self.user}
        """
