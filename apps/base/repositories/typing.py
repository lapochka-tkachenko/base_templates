from typing import TypeVar

from django.db.models import Model

TModel = TypeVar('TModel', bound=Model)
