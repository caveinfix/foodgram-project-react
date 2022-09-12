from rest_framework.validators import ValidationError

from recipes.models import Tag


def validate_tags(data):
    """Валидация тэгов: отсутствие в request, отсутствие в БД."""
    if not data:
        raise ValidationError({'tags': ['Обязательное поле.']})
    for tag in data:
        if not Tag.objects.filter(id=tag).exists():
            raise ValidationError({'tags': ['Неверный Тег']})
    return data