import json
import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET


def _icon_src(filename):
    """Relative URLs avoid localhost vs 127.0.0.1 mismatches in the manifest."""
    return f'{settings.STATIC_URL}pwa/icons/{filename}'


@require_GET
@cache_control(max_age=86400, public=True)
def manifest(request):
    icons = [
        ('72x72', 'icon-72.png'),
        ('96x96', 'icon-96.png'),
        ('128x128', 'icon-128.png'),
        ('144x144', 'icon-144.png'),
        ('152x152', 'icon-152.png'),
        ('192x192', 'icon-192.png'),
        ('384x384', 'icon-384.png'),
        ('512x512', 'icon-512.png'),
    ]
    site_url = getattr(settings, 'ADMSS_SITE_URL', '').rstrip('/')
    manifest_data = {
        'id': site_url + '/' if site_url else '/',
        'name': settings.PWA_APP_NAME,
        'short_name': settings.PWA_APP_SHORT_NAME,
        'description': settings.PWA_APP_DESCRIPTION,
        'start_url': settings.PWA_START_URL,
        'scope': '/',
        'display': 'standalone',
        'orientation': 'any',
        'background_color': settings.PWA_BACKGROUND_COLOR,
        'theme_color': settings.PWA_THEME_COLOR,
        'icons': [
            {
                'src': _icon_src(filename),
                'sizes': size,
                'type': 'image/png',
                'purpose': 'any',
            }
            for size, filename in icons
        ],
    }
    return HttpResponse(
        json.dumps(manifest_data, indent=2),
        content_type='application/manifest+json; charset=utf-8',
    )


@require_GET
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def service_worker(request):
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'pwa', 'service-worker.js')
    with open(sw_path, encoding='utf-8') as sw_file:
        content = sw_file.read()
    return HttpResponse(content, content_type='application/javascript')


@require_GET
def offline(request):
    return render(request, 'includes/pwa_offline.html')
