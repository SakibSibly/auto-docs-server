from decouple import config

# Fallback to 'local' if DJANGO_ENV is not set
env = config("DJANGO_ENV")

if env == 'production':
    from .production import *
else:
    from .local import *
