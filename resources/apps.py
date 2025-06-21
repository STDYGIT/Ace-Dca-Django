from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resources'
    verbose_name = 'Department Resources'  # Name shown in admin panel

    def ready(self):
        import resources.signals  # Import the signals
