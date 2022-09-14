from django.contrib import admin

from .models import (
    Ingredient,
    Recipe,
    Tag,
    IngredientRecipe,
    Favorite,
    Shopping,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "favorite",
        "author",
    )
    search_fields = (
        "name",
        "author__username",
    )
    list_filter = ("tags", "author")

    @admin.display(description="В избранном")
    def favorite(self, obj):
        return obj.favorite.count()


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")


@admin.register(Shopping)
class ShoppingAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
