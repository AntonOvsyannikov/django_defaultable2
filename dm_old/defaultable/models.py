# coding=utf-8
from __future__ import absolute_import

import os
from abc import abstractmethod
from functools import partial

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.db import models, IntegrityError
from django.db.models import Q
from django.db.models.signals import pre_delete

from dm.shared import ensure_dir


class Defaultable(models.Model):
    class Meta:
        abstract = True

    isDefault = models.BooleanField(default=False)

    @classmethod
    def default(cls):
        from .stuff import get_or_create_default
        return partial(get_or_create_default, cls.__name__, cls._meta.app_label)

    @classmethod
    def ForeignKey(cls, **kwargs):
        return models.ForeignKey(cls, default=cls.default(), on_delete=models.SET_DEFAULT)

    # take care of data integrity
    def __init__(self, *args, **kwargs):
        super(Defaultable, self).__init__(*args, **kwargs)

        # noinspection PyShadowingNames,PyUnusedLocal
        def pre_delete_defaultable(instance, **kwargs):
            if instance.isDefault:
                raise IntegrityError, "Can not delete default object {}".format(instance.__class__.__name__)

        pre_delete.connect(pre_delete_defaultable, self.__class__, weak=False, dispatch_uid=self._meta.db_table)

    def save(self, *args, **kwargs):
        super(Defaultable, self).save(*args, **kwargs)
        if self.isDefault:  # Ensure only one default, so make all others non default
            self.__class__.objects.filter(~Q(id=self.id), isDefault=True).update(isDefault=False)
        else:  # Ensure at least one default exists
            if not self.__class__.objects.filter(isDefault=True).exists():
                self.__class__.objects.filter(id=self.id).update(isDefault=True)

    @property
    def mark(self):
        # noinspection PyTypeChecker
        return ['', '*'][self.isDefault]

# ===========================================

class OverwriteStorage(get_storage_class()):

    def _save(self, name, content):
        self.delete(name)
        return super(OverwriteStorage, self)._save(name, content)

    def get_available_name(self, name, max_length=None):
        return name


# -------------------------------------------


def upload_to(self, fn):
    return self.upload_to(fn)


# -------------------------------------------

class WithFileFields(models.Model):
    class Meta:
        abstract = True

    # Set to True if need to transfer files in new directory
    # Set to False after transver to avoid productivity loss
    relocate_files = False

    @abstractmethod
    def upload_to(self, fn):
        """
        Returns full name of the file associated with this field. Can contain id and
        all other attributes known **after** model.save().
        :param fn: filename
        :return: file name with path, related to MEDIA_ROOT
        :rtype: str
        """
        pass

    def prepare_path(self, fn):
        fn = self.upload_to(fn)
        path = os.path.join(settings.MEDIA_ROOT, fn)
        ensure_dir(path)
        return fn, path

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            saved = []
            for f in self.__class__._meta.get_fields():
                if isinstance(f, models.FileField):
                    saved.append((f.name, getattr(self, f.name)))
                    setattr(self, f.name, None)

            super(WithFileFields, self).save(force_insert, force_update, using, update_fields)

            for name, val in saved:
                setattr(self, name, val)

        super(WithFileFields, self).save(False, force_update, using, update_fields)

        if self.relocate_files:  # чтобы переносить файлы при записи надо добавить это поле

            for f in [f for f in self.__class__._meta.get_fields() if isinstance(f, models.FileField)]:

                # noinspection PyShadowingNames
                upload_to = f.upload_to

                f = getattr(self, f.name)  # f is FileField now

                if f and callable(upload_to):
                    _, fn = os.path.split(f.name)
                    old_name = os.path.normpath(f.name)
                    new_name = os.path.normpath(upload_to(self, fn))

                    if old_name != new_name:

                        old_path = os.path.join(settings.MEDIA_ROOT, old_name)
                        new_path = os.path.join(settings.MEDIA_ROOT, new_name)

                        new_dir, _ = os.path.split(new_path)
                        if not os.path.exists(new_dir):
                            print "Making  dir {}", new_dir
                            os.makedirs(new_dir)

                        print "Moving {} to {}".format(old_path, new_path)
                        try:
                            os.rename(old_path, new_path)
                            f.name = new_name

                        except WindowsError as e:
                            print "Can not move file, WindowsError: {}".format(e)
            super(WithFileFields, self).save(False, force_update, using, update_fields)



def save_to_filefield(s, model, field_name, file_name):

    fld = model.__class__._meta.get_field(field_name)
    name = fld.upload_to(model, file_name) if callable(fld.upload_to) else os.path.join(fld.upload_to, file_name)
    path = os.path.join(settings.MEDIA_ROOT, name)
    ensure_dir(path)

    with open(path, "wb") as f:
        f.write(s)

    getattr(model,field_name).name = name
    model.save()
