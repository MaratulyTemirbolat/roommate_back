# Django
from django.db.models import (
    CharField,
    ForeignKey,
    CASCADE,
)

# Project
from abstracts.models import AbstractDateTime


class Category(AbstractDateTime):
    """Category model database."""

    CATEGORY_NAME_LIMIT = 200

    name: CharField = CharField(
        max_length=CATEGORY_NAME_LIMIT,
        db_index=True,
        unique=True,
        verbose_name="Наименование категории"
    )

    class Meta:
        """Customization of the DB table."""

        verbose_name: str = "Категория"
        verbose_name_plural: str = "Категории"

    def __str__(self) -> str:
        return f"Категория: \"{self.name}\""


class SubCategory(AbstractDateTime):
    """SubCategory model database entity."""

    SUBCATEGORY_NAME_LIMIT = 200

    name: CharField = CharField(
        max_length=SUBCATEGORY_NAME_LIMIT,
        db_index=True,
        unique=True,
        verbose_name="Название под-категории"
    )
    main_category: Category = ForeignKey(
        to=Category,
        on_delete=CASCADE,
        related_name="sub_categories",
        verbose_name="Категория"
    )

    class Meta:
        """Customization of the DB table."""

        verbose_name: str = "Под категория"
        verbose_name_plural: str = "Под категории"
        ordering: tuple[str] = ("-datetime_updated",)

    def __str__(self) -> str:
        return f"Под категория: \"{self.name}\""
