from turtle import color

from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin
from .models import Brand, Category, Color, Product, ProductVariant, Size

# django-image-uploader-widget


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = (
        "tree_actions",
        "indented_title",
        "slug",
        "is_active",
        "order",
        "created_at",
    )
    list_filter = ("is_active", "parent")
    search_fields = ("name", "slug")
    list_editable = ("is_active", "order")
    list_display_links = ("indented_title",)
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        (None, {"fields": ("name", "slug", "parent", "image", "is_active", "order")}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        return super().save_model(request, obj, form, change)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    # Тут настроить фото
    list_display = ("name", "is_active", "logo_preview")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        (
            None,
            {"fields": ("name", "slug", "logo", "description", "is_active")},
        ),
    )

    @admin.display(description="Лого")
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:50px;" />', obj.logo.url)
        return "-"


@admin.register(Size)
class SizeTypeAdmin(admin.ModelAdmin):
    list_display = ("value", "size_type", "order")
    list_editable = ("order",)
    list_filter = ("size_type",)
    ordering = (
        "size_type",
        "order",
    )
    search_fields = ("value",)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "color",
        "size",
        "stock",
        "sku",
        "price_override",
    )
    autocomplete_fields = (
        "color",
        "size",
    )
    verbose_name = "Вариант товара"
    verbose_name_plural = "Варианты товара"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "brand",
        "gender",
        "price",
        "discount",
        "final_price_display",
        "is_active",
        "total_stock",
    )
    list_editable = ("is_active", "price", "discount")
    list_filter = ("is_active", "gender", "category", "brand")
    search_fields = ("name", "slug", "description")
    autocomplete_fields = ("category", "brand")
    readonly_fields = ("public_id",)
    inlines = (ProductVariantInline,)
    prepopulated_fields = {"slug": ("name",)}
    list_select_related = ("category", "brand")

    def get_queryset(self, request):
        return (
            super()
            .get_queyset(request)
            .select_related("category", "brand")
            .annotate(_total_stock=Sum("variant__stock"))
        )

    @admin.display(description="Цены со скидкой")
    def final_price_display(self, obj):
        return obj.final_price

    @admin.display(description="Остаток (Всего)", ordering="_total_stock")
    def total_stock(self, obj):
        return obj._total_stock or 0


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "color",
        "size",
        "stock",
        "sku",
        "is_available",
        "price_override",
    )
    list_editable = ("stock", "sku", "price_override")
    list_filter = ("size", "size__size_type")
    search_fields = ("product__name", "sku")
    autocomplete_fields = ("product", "size", "color")
    list_select_related = ("product", "color", "size")

    @admin.display(description="В наличии", boolean=True)
    def is_available(self, obj):
        return obj.stock > 0


@admin.register(Color)
class ColorProductAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "hex_code", "color_preview")
    search_fields = ("name", "hex_code")
    list_filter = ("name",)
    list_editable = ("hex_code",)
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = ((None, {"fields": ("name", "slug", "hex_code")}),)

    @admin.display(description="Цвет")
    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width:30px; height:30px; background:{}; border:1px solid #ccc; border-radius:4px;"></div>',
                obj.hex_code,
            )
        return "-"

