from django.core.management.base import BaseCommand, CommandError
from django.apps import apps

import os
import tempfile
import subprocess


class Command(BaseCommand):
    help = "python manage.py edit <app.model.field> <pk>"

    def add_arguments(self, parser):
        parser.add_argument('model')
        parser.add_argument('id')

    def handle(self, *args, **options):
        app_label, model_name, field_name = options.get('model').split('.', 2)

        try:
            model = apps.get_model(app_label, model_name)
        except Exception:
            raise CommandError("Failed to load model")

        try:
            obj = model.objects.get(pk=options.get('id'))
        except Exception:
            raise CommandError("Row with given id not found")

        f = tempfile.NamedTemporaryFile('w+t', delete=False)
        filename = f.name

        f.write(getattr(obj, field_name))
        f.close()

        mtime = os.path.getmtime(filename)

        try:
            subprocess.check_call(["vim", filename])
        except Exception:
            raise CommandError("Failed to launch external editor.")

        if mtime < os.path.getmtime(filename):
            setattr(obj, field_name, open(filename).read())
            obj.save()

        os.unlink(filename)
