# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from dm.defaultable.models import Defaultable, WithFileFields, upload_to



class ModelX(Defaultable, WithFileFields):
    f = models.FileField(default='*myfile.txt', upload_to=upload_to, max_length=1024)

    def upload_to(self, fn):
        return 'modelxs/{}/{}'.format(self.id, fn)

    def __unicode__(self):
        return "{}X{}:{}".format(self.mark, self.id, self.f)


# class ModelY(Defaultable):
#     def __unicode__(self):
#         return "{}Y{}".format(self.mark, self.id)

# -------------------------------------------

class MyModel(models.Model):
    x = ModelX.ForeignKey()

    # y = ModelY.ForeignKey()

    # def __unicode__(self):
    #     return "M{}:x={}".format(self.id, self.x)

    # def __unicode__(self):
    #     return "M{}:y={}".format(self.id, self.y)
    pass
