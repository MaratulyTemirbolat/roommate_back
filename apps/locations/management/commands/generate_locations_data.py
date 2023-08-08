# Python
from datetime import datetime
from typing import (
    Any,
    Tuple,
    Dict,
)

# Django
from django.core.management.base import BaseCommand

# Project
from locations.models import (
    City,
    District,
)


class Command(BaseCommand):
    """Custom command for filling up database."""

    __CITIES = (
        "Алматы",
    )
    __DISTRICTS = (
        "Алатауский",
        "Алмалинский",
        "Ауэзовский",
        "Бостандыкский",
        "Жетысуский",
        "Наурызбайский",
        "Турксибский",
    )

    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        """Call parent constructor."""
        super().__init__(args, kwargs)

    def _generate_cities(self) -> None:
        """Generate test cities."""
        existed_cities: int = City.objects.all().count()
        if existed_cities == 0:
            name: str
            for name in self.__CITIES:
                City.objects.get_or_create(name=name)
            print("Все города успешно созданы")

    def _generate_districts(self) -> None:
        existed_cities: int = City.objects.all().count()
        existed_districts: int = District.objects.all().count()
        if existed_cities != 0 and existed_districts == 0:
            almaty_id: int = City.objects.values_list("id", flat=True)[0]
            name: str
            for name in self.__DISTRICTS:
                District.objects.get_or_create(
                    name=name,
                    city_id=almaty_id
                )
            print("Все районы успешно созданы")

    def handle(self, *args: Tuple[Any], **options: Dict[str, Any]) -> None:
        """Handle data filling."""
        start_time: datetime = datetime.now()

        # Data generation
        self._generate_cities()
        self._generate_districts()

        print(
            "Генерация данных составила: {} секунд".format(
                (datetime.now()-start_time).total_seconds()
            )
        )
