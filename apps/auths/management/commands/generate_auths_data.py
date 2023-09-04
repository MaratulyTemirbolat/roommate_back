# Third party
from names import (
    get_first_name,
    get_last_name,
)
# Python
from datetime import datetime
from random import (
    choice,
    randint,
    sample,
)
from typing import (
    Any,
    Tuple,
    Dict,
)

# Django
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db.models import QuerySet

# Project
from auths.models import CustomUser
from locations.models import District
from events.models import SubCategory


class Command(BaseCommand):
    """Custom command for filling up database."""

    __email_patterns: Tuple[str] = (
        "mail.ru", "gmail.com", "outlook.com", "yahoo.com",
        "inbox.ru", "yandex.kz", "yandex.ru", "mail.kz",
    )
    __message_template_parts: tuple[str] = (
        "hello", "world", "animal", "person",
        "good", "thank you", "nice", "show", "say",
        "anime", "Turkey", "Canada", "Kazakhstan", "dear",
        "bird", "dog", "cat", "queen", "buy", "sir", "apple",
        "pear", "zebra", "man", "girl", "boy", "Russia",
        "Paris", "United Kingdom", "boyfriend", "girlfriend",
        "Kaneki", "John", "Temirbolat", "Mike", "Marat", "Rem",
        "Ram", "laptop", "computer", "mouse", "lorem impsum",
        "Almaty", "Moscow", "Astana", "Karaganda", "NU", "KBTU",
        "or", "and", "as well as", "along with", "while", "including",
    )
    __phone_beginning: Tuple[str] = (
        "+7",
        "8",
    )
    __mobile_provider_phones: Tuple[str] = (
        "778", "701", "775", "702",
        "775", "747", "707", "771",
    )
    __email_devider: Tuple[str] = ("_", ".",)
    __STATES = (True, False,)
    __GENDERS = ("M", "F")
    PASSWORD_PATTERN = "12345"

    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        """Call parent constructor."""
        super().__init__(args, kwargs)

    def __generate_users(self, required_number: int = 0) -> None:
        def get_email(first_name: str, last_name: str) -> str:
            email_pattern: str = choice(self.__email_patterns)
            return "{0}@{1}".format(
                first_name.lower() +
                choice(self.__email_devider) +
                last_name.lower(),
                email_pattern
            )

        def get_comment() -> str:
            MIN_CONTENT_WORDS_NUM = 5
            MAX_CONTENT_WORDS_NUM = 30
            ran_words_number: int = randint(
                MIN_CONTENT_WORDS_NUM,
                MAX_CONTENT_WORDS_NUM
            )
            return " ".join(
                sample(
                    population=self.__message_template_parts,
                    k=ran_words_number
                )
            ).capitalize()

        def get_phone() -> str:
            res_phone: str = choice(
                self.__phone_beginning
            ) + choice(
                self.__mobile_provider_phones
            ) + str(
                randint(100, 999)
            ) + str(
                randint(10, 99)
            ) + str(
                randint(10, 99)
            )
            return res_phone

        def get_telegram_username(first_name: str, last_name: str) -> str:
            return (
                first_name.lower() +
                choice(self.__email_devider) +
                last_name.lower()
            )

        def get_gender() -> str:
            return choice(self.__GENDERS)

        def get_is_active() -> bool:
            return choice(self.__STATES)

        def get_month_budjet() -> int:
            return randint(10000, 100000)

        def get_name() -> str:
            return get_first_name()

        def get_surname() -> str:
            return get_last_name()

        def generate_password() -> str:
            return make_password(self.PASSWORD_PATTERN)

        users_cnt: int = 0
        obj: CustomUser
        is_created: bool = False
        districts: QuerySet[District] | tuple[District] = \
            District.objects.all()
        distr_number: int = districts.count()
        districts = tuple(districts)

        hobby_subcategories: QuerySet[SubCategory] | tuple[SubCategory] = \
            SubCategory.objects.all()
        categories_number: int = hobby_subcategories.count()
        hobby_subcategories = tuple(hobby_subcategories)

        _: int
        for _ in range(required_number):

            first_name: str = get_name()
            last_name: str = get_surname()
            email: str = get_email(
                first_name=first_name,
                last_name=last_name
            )
            phone: str = get_phone()
            telegram_username: str = get_telegram_username(
                first_name=first_name,
                last_name=last_name
            )
            gender: str = get_gender()
            is_active: bool = get_is_active()
            month_budjet: int = get_month_budjet()
            comment: str = get_comment()
            obj, is_created = CustomUser.objects.get_or_create(
                email=email,
                phone=phone,
                first_name=first_name,
                telegram_username=telegram_username,
                gender=gender,
                is_active=is_active,
                month_budjet=month_budjet,
                comment=comment,
                password=generate_password()
            )
            if is_created:
                districts_number: int = randint(1, distr_number)
                categories_number: int = randint(1, categories_number)

                distr: District
                for distr in sample(districts, k=districts_number):
                    obj.districts.add(distr)

                subcat: SubCategory
                for subcat in sample(hobby_subcategories, k=categories_number):
                    obj.hobby_categories.add(subcat)

                users_cnt += 1
        print(f"{users_cnt} пользователей успешно созданы")

    def handle(self, *args: Tuple[Any], **options: Dict[str, Any]) -> None:
        """Handle data filling."""
        start_time: datetime = datetime.now()

        # CustomUser data generation
        USERS_NUMBER = 100
        self.__generate_users(required_number=USERS_NUMBER)

        print(
            "Генерация данных составила: {} секунд".format(
                (datetime.now()-start_time).total_seconds()
            )
        )
