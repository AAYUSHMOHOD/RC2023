from django.apps import AppConfig

# Incluting all Apps (One in this case)
class myapp_RCConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp_RC'