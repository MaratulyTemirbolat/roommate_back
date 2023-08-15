from typing import (
    Tuple,
    Any,
)

from django.db.models import (
    CharField,
    UniqueConstraint,
    ForeignKey,
    CASCADE,
)

from abstracts.models import AbstractDateTime


class City(AbstractDateTime):
    """City table model in Database."""
    CITY_NAME_LIMIT = 200

    name: CharField = CharField(
        max_length=CITY_NAME_LIMIT,
        db_index=True,
        unique=True,
        verbose_name="Название города"
    )

    class Meta:
        """Customization of the DB table."""

        verbose_name: str = "Город"
        verbose_name_plural: str = "Города"
        ordering: Tuple[str] = ("-datetime_updated", "pk",)

    def __str__(self) -> str:
        return self.name


class District(AbstractDateTime):
    """District table model in Database."""
    DISTRICT_NAME_LIMIT = 254

    name: CharField = CharField(
        max_length=DISTRICT_NAME_LIMIT,
        unique=True,
        verbose_name="Наименование района"
    )
    city: City = ForeignKey(
        to=City,
        on_delete=CASCADE,
        related_name="districts",
        verbose_name="Город"
    )

    class Meta:
        """Customization of the Table."""

        verbose_name: str = "Район"
        verbose_name_plural: str = "Районы"
        ordering: Tuple[str] = ("-datetime_updated", "pk")
        constraints: Tuple[Any] = [
            UniqueConstraint(
                fields=['name', 'city'],
                name="unique_district_city"
            ),
        ]

    def __str__(self) -> str:
        return self.name
