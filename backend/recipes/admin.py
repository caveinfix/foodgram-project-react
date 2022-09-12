from django.contrib import admin
from .models import Recipe, Ingredient, Tag, IngredientRecipe
from users.models import User, Follow


# class RecipeIngredientsAdmin(admin.StackedInline):
#     model = IngredientRecipe
#     autocomplete_fields = ('ingredients',)



class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username",)

class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    # inlines = (RecipeIngredientsAdmin,)

class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "amount")




admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(User, UserAdmin)
