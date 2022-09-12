from django.db import models
from users.models import User


class Tag(models.Model):
    "Модель тэгов."
    name = models.CharField("Имя", max_length=16, unique=True)
    color = models.CharField("Цвет HEX", max_length=8, unique=True)
    slug = models.SlugField("Slug", unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    "Модель ингридиентов."
    name = models.CharField("Название ингридиента", max_length=40)
    measurement_unit = models.CharField("Масса ингридиента", max_length=16)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    "Модель рецепта."
    author = models.ForeignKey(
        User, related_name="recipes", on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientRecipe",
        related_name="recipes",
    )
    tags = models.ManyToManyField(Tag, related_name="recipes")
    name = models.CharField("Название", max_length=16)
    text = models.TextField("Описание рецепта")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления", default=1
    )

    image = models.ImageField(upload_to="recipes/images/", null=True)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    "Модель для связи id рецепта и id ингридиента."
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
    )
    amount = models.PositiveIntegerField(default=1)


class TagRecipe(models.Model):
    "Модель для связи id рецепта и id тэга."
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="tag_recipe",
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tag_recipe",
    )


class Favorite(models.Model):
    "Модель для избранного."
    user = models.ForeignKey(
        User,
        related_name="favorite",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="favorite",
        on_delete=models.CASCADE,
    )
    constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='favorite_recipes_for_unique_user')
        ]
    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'

# class Favorite(models.Model):
#     "Модель для избранного."
#     user = models.ForeignKey(
#         User,
#         related_name="favorite",
#         on_delete=models.CASCADE,
#     )
#     recipe = models.ForeignKey(
#         Recipe,
#         related_name="favorite",
#         on_delete=models.CASCADE,
#     )
#     constraints = [
#             models.UniqueConstraint(fields=('user', 'recipe'),
#                                     name='favorite_recipes_for_unique_user')
#         ]
#     def __str__(self):
#         return f'{self.recipe} в избранном у {self.user}'


class Shopping(models.Model):
    "Модель для избранного."
    user = models.ForeignKey(
        User,
        related_name="shopping_cart",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name="shopping_cart",
        on_delete=models.CASCADE,
    )
    constraints = [
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='favorite_recipes_for_unique_user')
        ]
    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'

