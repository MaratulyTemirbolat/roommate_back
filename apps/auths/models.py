# Python
from typing import (
    Optional,
    Any,
)
from requests import (
    Response,
    get,
)

# Django
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import (
    EmailField,
    CharField,
    BooleanField,
    IntegerField,
    BigIntegerField,
    TextField,
    ImageField,
    ManyToManyField,
    QuerySet,
    Q,
)

# Project
from abstracts.models import AbstractDateTime
from locations.models import District
from events.models import SubCategory
from auths.validators import validate_negative_price


class CustomUserManager(BaseUserManager):
    """CustomUserManger."""

    def __obtain_user_instance(
        self,
        email: str,
        phone: str,
        first_name: str,
        telegram_username: str,
        gender: int,
        password: str,
        month_budjet: int,
        comment: Optional[str] = None,
        photo: Optional[Any] = None,
        **kwargs: dict[str, Any]
    ) -> 'CustomUser':
        """Get user instance."""
        if not email:
            raise ValidationError(
                message="Email field is required",
                code="email_empty"
            )
        if first_name.replace(" ", "") == "":
            raise ValidationError(
                message="First name is required.",
                code="firt_name_empty"
            )

        new_user: 'CustomUser' = self.model(
            email=self.normalize_email(email),
            phone=phone,
            first_name=first_name,
            telegram_username=telegram_username,
            gender=gender,
            month_budjet=month_budjet,
            comment=comment,
            photo=photo,
            password=password,
            **kwargs
        )
        return new_user

    def create_user(
        self,
        email: str,
        phone: str,
        first_name: str,
        telegram_username: str,
        gender: int,
        password: str,
        month_budjet: int,
        comment: Optional[str] = None,
        photo: Optional[Any] = None,
        **kwargs: dict[str, Any]
    ) -> 'CustomUser':
        """Create Custom user."""
        new_user: 'CustomUser' = self.__obtain_user_instance(
            email=email,
            phone=phone,
            first_name=first_name,
            telegram_username=telegram_username,
            gender=gender,
            month_budjet=month_budjet,
            comment=comment,
            photo=photo,
            password=password,
            **kwargs
        )
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user

    def create_superuser(
        self,
        email: str,
        first_name: str,
        password: str,
        **kwargs: dict[str, Any]  # kwargs -> key word arguments
    ) -> 'CustomUser':
        """Create super user."""
        new_user: 'CustomUser' = self.__obtain_user_instance(
            email=email,
            first_name=first_name,
            password=password,
            **kwargs
        )
        new_user.is_staff = True
        new_user.is_superuser = True
        new_user.set_password(password)
        new_user.save(using=self._db)
        return new_user

    def get_deleted(self) -> QuerySet:
        """Get deleted users."""
        return self.filter(
            datetime_deleted__isnull=False
        )

    def get_not_deleted(self) -> QuerySet:
        """Get not deleted users."""
        return self.filter(
            datetime_deleted__isnull=True
        )

    def get_by_email_phone_telegram(
        self,
        phone_email_telegram: str
    ) -> Optional["CustomUser"]:
        """Get CustomUser instance by email phone or telegram username."""
        custom_user: Optional["CustomUser"] = None

        try:
            custom_user = self.get(
                Q(email=phone_email_telegram) |
                Q(phone=phone_email_telegram) |
                Q(telegram_username=phone_email_telegram)
            )
            return custom_user
        except CustomUser.DoesNotExist:
            return None


class CustomUser(
    AbstractBaseUser,
    PermissionsMixin,
    AbstractDateTime
):
    """CustomUser model database."""
    EMAIL_MAX_LEN = 254
    FIRST_NAME_LEN = 254
    TELEGRAM_USERNAME_LEN = 254
    GENDER_MAX_LEN = 1
    TELEGRAM_ID_LEN = 30
    SINGLE_FIELDS = (
        "email", "phone",
        "first_name", "telegram_username",
        "gender", "month_budjet",
        "comment", "password",
        "telegram_user_id",
    )
    GENDERS = (
        ("M", "Male"),
        ("F", "Female"),
    )

    email: EmailField = EmailField(
        max_length=EMAIL_MAX_LEN,
        unique=True,
        db_index=True,
        verbose_name="Почта"
    )
    phone: CharField = CharField(
        max_length=15,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$",  # noqa
                message="Номер телефона введен неправильно",
                code="phone_template_error"
            )
        ],
        verbose_name="Номер телефона"
    )
    first_name: CharField = CharField(
        max_length=FIRST_NAME_LEN,
        verbose_name="Имя"
    )
    telegram_username: CharField = CharField(
        max_length=TELEGRAM_USERNAME_LEN,
        db_index=True,
        unique=True,
        null=True,
        verbose_name="Имя пользователя Telegram"
    )
    telegram_user_id: BigIntegerField = BigIntegerField(
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name="Идентификатор пользователя в телеграм"
    )
    gender: CharField = CharField(
        max_length=GENDER_MAX_LEN,
        choices=GENDERS,
        verbose_name="Пол пользователя"
    )
    is_active: BooleanField = BooleanField(
        default=True,
        verbose_name="Активность",
        help_text="True - ваш акк активный, False - удален"
    )
    month_budjet: IntegerField = IntegerField(
        validators=[validate_negative_price],
        verbose_name="Месячный бюджет"
    )
    comment: TextField = TextField(
        null=True,
        blank=True,
        verbose_name="Комментарий"
    )
    photo: ImageField = ImageField(
        upload_to="photos/profile_photos/%Y/%m/%d",
        blank=True,
        null=True,
        verbose_name="Фото профиля"
    )
    districts: ManyToManyField = ManyToManyField(
        to=District,
        related_name="users",
        verbose_name="Районы"
    )
    hobby_categories: ManyToManyField = ManyToManyField(
        to=SubCategory,
        related_name="users",
        verbose_name="Категории хобби"
    )
    is_staff: BooleanField = BooleanField(
        default=False,
        verbose_name="Статус менеджера"
    )
    is_active_account: BooleanField = BooleanField(
        default=True,
        verbose_name="Состояние аккаунта"
    )
    is_confirmed_account: BooleanField = BooleanField(
        default=False,
        verbose_name="Подтверждение, что действительно человек"
    )
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list[str] = [
        "phone",
        "first_name",
        "telegram_username",
        "gender",
        "month_budjet",
    ]

    class Meta:
        """Customization of the Model (table)."""

        ordering: tuple[str] = (
            "-datetime_updated",
        )
        verbose_name: str = "Пользователь"
        verbose_name_plural: str = "Пользователи"

    def __str__(self) -> str:
        return self.email

    def deactivate(self, *args: tuple[Any], **kwargs: dict[str, Any]) -> None:
        """Deactivate user."""
        if self.is_active_account:
            self.is_active_account = False
            self.save(
                update_fields=['is_active_account']
            )

    def activate(self, *args: tuple[Any], **kwargs: dict[str, Any]) -> None:
        """Actovate user."""
        if not self.is_active_account:
            self.is_active_account = True
            self.save(
                update_fields=['is_active_account']
            )

    def recover(self, *args: tuple[Any], **kwargs: dict[str, Any]) -> None:
        """Recover the user if he is deleted."""
        if self.datetime_deleted:
            self.datetime_deleted = None
            self.save(
                update_fields=['datetime_deleted']
            )

    def save_remote_image(self, image_url: str) -> None:
        """Save remote image for photo if it's not provided."""
        if not self.photo:
            resp: Response = get(url=image_url)
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(resp.content)
            img_temp.flush()

            self.photo.save(
                name=f"{self.email}.jpg",
                content=File(img_temp),
                save=True
            )

    def confirm_account(self) -> None:
        """Confirm user's account as a real person."""
        if not self.is_confirmed_account:
            self.is_confirmed_account = True
            self.save(
                update_fields=['is_confirmed_account']
            )
