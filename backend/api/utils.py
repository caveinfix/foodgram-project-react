from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipe


def post_method(request, pk, get_serializer):
    user = request.user
    recipe = get_object_or_404(Recipe, pk=pk)
    serializer = get_serializer(
        data={"user": user.id, "recipe": recipe.id},
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_method(request, pk, get_model):
    object = get_object_or_404(
        get_model,
        recipe=get_object_or_404(Recipe, pk=pk),
        user=request.user,
    )
    object.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
