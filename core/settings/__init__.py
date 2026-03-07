import os

ENVIRONMENT = os.getenv('DJANGO_ENV', 'dev')

if ENVIRONMENT == 'prod':
    from core.settings.prod import *
else:
    from core.settings.local import *
