import uuid
from decimal import Decimal
from autoslug import AutoSlugField
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    PositiveIntegerField,
    TextField,
    UUIDField,
    Q,
)
from mptt.models import MPTTModel, TreeForeignKey

from src.utils.slug import translit_slugify


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SlugMixin(models.Model):
    class Meta:
        abstract = True

    slug = AutoSlugField(
        populate_from="name",
        unique=True,
        always_update=True,
        max_length=100,
        editable=True,
        slugify=translit_slugify,
    )


class IsActiveMixin(models.Model):
    is_active = BooleanField(default=True)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created_at = DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True


class Category(SlugMixin, TimeStampedMixin, IsActiveMixin, MPTTModel):
    active = ActiveManager()
    name = CharField(max_length=50, unique=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
    )
    image = ImageField(null=True, blank=True, upload_to="categories-image/%Y/%m/%d")
    order = PositiveIntegerField(default=0)

    class MPTTMeta:
        order_insertion_by = ["order", "name"]

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Brand(SlugMixin, TimeStampedMixin, IsActiveMixin, models.Model):
    active = ActiveManager()
    name = CharField(max_length=50, unique=True)
    logo = ImageField(upload_to="brand-logo/%Y/%m/%d", blank=True, null=True)
    description = TextField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SizeType(models.TextChoices):
    CLOTHING = "clothing", "Одежда"
    SHOES = "shoes", "Обувь"
    UNIVERSAL = "universal", "Без размера"


class Size(models.Model):
    size_type = CharField(max_length=20, choices=SizeType.choices)
    value = CharField(max_length=10)
    order = PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"
        constraints = (
            models.UniqueConstraint(
                fields=("size_type", "value"), name="unique_size_constraint"
            ),
        )
        ordering = ["size_type", "order"]

    def __str__(self):
        return self.value


class Color(SlugMixin, models.Model):
    name = CharField(max_length=50, unique=True)
    hex_code = CharField(
        max_length=7,
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message="Цвет должен быть в формате HEX, например #FF0000",
            )
        ],
        verbose_name="HEX-код",
    )

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(SlugMixin, TimeStampedMixin, IsActiveMixin, models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Мужской"
        FEMALE = "female", "Женский"
        UNISEX = "unisex", "Унисекс"
        KIDS = "kids", "Детский"

    objects = models.Manager()
    active = ActiveManager()

    name = CharField(max_length=100, db_index=True)
    price = DecimalField(
        max_digits=20, decimal_places=2, validators=[MinValueValidator(Decimal("1"))]
    )
    discount = DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    sizes = ManyToManyField(Size, through="ProductVariant", related_name="products")
    description = TextField(max_length=300, blank=True)
    category = ForeignKey(
        Category, null=True, on_delete=models.SET_NULL, related_name="products"
    )
    brand = ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    gender = CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.UNISEX,
        db_index=True,
        verbose_name="Пол",
    )
    public_id = UUIDField(unique=True, default=uuid.uuid4, editable=False)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["brand", "gender"]),
            models.Index(fields=["is_active", "price"]),
        ]
        constraints = (
            models.CheckConstraint(
                condition=(Q(discount__gte=0) & Q(discount__lte=100)),
                name="discount_between_0_and_100",
            ),
            models.CheckConstraint(condition=Q(price__gte=1), name="price_gte_1"),
        )

    @property
    def final_price(self) -> Decimal:
        if self.discount:
            return (self.price * (1 - self.discount / 100)).quantize(Decimal("0.01"))
        return self.price

    def __str__(self):
        return self.name


class ProductVariant(TimeStampedMixin, models.Model):
    product = ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = ForeignKey(Size, on_delete=models.PROTECT)
    color = ForeignKey(
        Color, on_delete=models.PROTECT, related_name="variants", null=True, blank=True
    )
    stock = PositiveIntegerField(default=0)
    sku = CharField(max_length=64, unique=True)
    price_override = DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("1"))],
    )

    class Meta:
        verbose_name = "Вариант товаров"
        verbose_name_plural = "Вариант товаров"
        indexes = (
            models.Index(fields=["product", "stock"]),
            models.Index(fields=["product", "color"]),
        )
        constraints = (
            models.UniqueConstraint(
                fields=["product", "size", "color"], name="unique_product_size_color"
            ),
            models.CheckConstraint(
                condition=Q(price_override__gte=1) | Q(price_override__isnull=True),
                name="price_override_gte_1",
            ),
        )

    def __str__(self):
        parts = [self.product.name]
        if self.color_id:
            parts.append(str(self.color))
        if self.size:
            parts.append(str(self.size))

        return " - ".join(parts)

    @property
    def is_available(self):
        return self.stock > 0
