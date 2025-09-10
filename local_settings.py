# Пример local_settings
# Измените данные на свои

DEBUG = True
ALLOWED_HOSTS = ['*']

from integration_utils.bitrix24.local_settings_class import LocalSettingsClass

TINKOFF_API_KEY = 'your-api-key'
ENDPOINT_TINKOFF = 'your-secret-key'
API_KEY_TINKOFF = 'your-api-key'
SECRET_KEY_TINKOFF = 'your-secret-key'

OPEN_AI_API_KEY = 'your-api-key'

NGROK_URL='56218ef983f3-8301993767665431593.ngrok-free.app'

APP_SETTINGS = LocalSettingsClass(
    portal_domain='b24-p202z0.bitrix24.ru',
    app_domain='127.0.0.1:8000',
    app_name='deal_app',
    salt='wefiewofioiI(IF(Eufrew8fju8ewfjhwkefjlewfjlJFKjewubhybfwybgybHBGYBGF',
    secret_key='wefewfkji4834gudrj.kjh237tgofhfjekewf.kjewkfjeiwfjeiwjfijewf',
    application_bitrix_client_id='local.68bff495d51f94.96236588',
    application_bitrix_client_secret='Txv5IewGJbOkIv7ECKtQ5TPs3DDo2pLVhpzmjA9C71CtQqIdJu',
    application_index_path='/',
)

DOMAIN = "56218ef983f3-8301993767665431593.ngrok-free.app"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'foodgram',
        'USER': 'postgres',
        'PASSWORD': 'wa3499',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}