from django.conf import settings


def pwa(request):
    return {
        'PWA_APP_SHORT_NAME': getattr(settings, 'PWA_APP_SHORT_NAME', 'admss'),
        'PWA_THEME_COLOR': getattr(settings, 'PWA_THEME_COLOR', '#44444b'),
        'ADMSS_SITE_URL': getattr(settings, 'ADMSS_SITE_URL', ''),
    }
