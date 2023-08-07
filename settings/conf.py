from decouple import config

# ----------------------------------------------
# Enviromental variables
#
SECRET_KEY = config("SECRET_KEY", cast=str)

# ----------------------------------------------
# Custom settings
#
ADMIN_SITE_URL = config("ADMIN_SITE_URL", default="admin/", cast=str)

# ----------------------------------------------
# DRF settings
#
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     'rest_framework_simplejwt.authentication.JWTAuthentication',
    # )
}
