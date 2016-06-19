from django.db import models
from django.utils.translation import ugettext_lazy as _

from zkcluster.models import User

class Parent(models.Model):
    name = models.CharField(_('name'), max_length=200)
    phone_number = models.CharField(_('phone'), max_length=12)

    def __unicode__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, related_name='student')
