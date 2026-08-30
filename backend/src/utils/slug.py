from django.utils.text import slugify as django_slugify
from unidecode import unidecode


def translit_slugify(value: str) -> str:
    return django_slugify(unidecode(value), allow_unicode=False)
