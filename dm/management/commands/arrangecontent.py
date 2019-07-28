# coding=utf-8
"""
Упорядочивает содержимое базы.

1) Проходит по всем моделям с файловыми полями и раскладывает контент в актуальные папки,
в том числе заполняет поля с дефолтным контентом, если поля появиились во время миграций.

"""

from __future__ import absolute_import
from __future__ import unicode_literals

from django.apps import apps
from django.core.management.base import BaseCommand

from dm.defaultable.models import WithFileFields


class Command(BaseCommand):

    def handle(self, *args, **options):
        for m in filter(lambda cls: issubclass(cls, WithFileFields), apps.get_app_config('dm').get_models()):
            print 'Resaving {} object(s) for model {}:'.format(len(m.objects.all()), m.__name__)
            m.relocate_files = True
            for o in m.objects.all():
                o.save()
            print 'OK'

