import inspect
from django.db import models

def buscar_todos_enums():
    """
    Procura automaticamente todas as subclasses de TextChoices
    nos apps instalados.
    """
    from django.apps import apps

    enums = {}

    for app_config in apps.get_app_configs():
        try:
            module = __import__(f"{app_config.name}.models.enums", fromlist=[''])
        except ModuleNotFoundError:
            continue  # app sem enums.py → ignora

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, models.TextChoices):
                enums[name] = [
                    {"value": choice[0], "label": choice[1]}
                    for choice in obj.choices
                ]

    return enums