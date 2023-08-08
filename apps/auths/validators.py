# Django
from django.core.exceptions import ValidationError


def validate_negative_price(price: int = 0):
    if price < 0:
        raise ValidationError(
            message="Вы не можете устанавливать отрицательную сумму",
            code="neg_price_error"
        )
