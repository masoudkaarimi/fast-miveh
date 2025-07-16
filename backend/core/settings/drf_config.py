from datetime import timedelta

# --- Django Rest Framework ---
REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     # 'rest_framework.permissions.IsAuthenticated',
    # ],
    # 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'VERSION_PARAM': 'version',
}

# --- Simple JWT Configuration ---
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),

    # # 'ROTATE_REFRESH_TOKENS': False,
    # # 'BLACKLIST_AFTER_ROTATION': True,
    # 'UPDATE_LAST_LOGIN': True,

    # # 'ALGORITHM': 'HS256',
    # # 'SIGNING_KEY': SECRET_KEY,
    # # 'VERIFYING_KEY': None,
    # # 'AUDIENCE': None,
    # # 'ISSUER': None,
    # # 'JWK_URL': None,
    # # 'LEEWAY': 0,

    # # 'AUTH_HEADER_TYPES': ('Bearer',),
    # # 'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    # # 'USER_ID_FIELD': 'id',
    # # 'USER_ID_CLAIM': 'user_id',
    # # 'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    # # 'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    # # 'TOKEN_TYPE_CLAIM': 'token_type',
    # # 'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    # # 'JTI_CLAIM': 'jti',

    # # 'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # # 'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    # # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# --- Spectacular Configuration ---
SPECTACULAR_SETTINGS = {
    # 'TITLE': 'Your Project API',
    # 'DESCRIPTION': 'Your project description',
    # 'VERSION': '1.0.0',
    # 'SERVE_INCLUDE_SCHEMA': False,
}
