from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModelTimeStamp(models.Model):
    creation_date = models.DateTimeField(_('Creation Date'), auto_now_add=True)
    update_date = models.DateTimeField(_('Update Date'), auto_now=True)

    class Meta:
        abstract = True
