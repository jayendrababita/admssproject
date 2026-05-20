from django.apps import AppConfig


class AdmssappConfig(AppConfig):
    name = 'admssapp'

    def ready(self):
        import admssapp.signals
