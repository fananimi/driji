from django.db import models
from django.utils.translation import ugettext_lazy as _

from zkcluster.models import User as ZKUser

class BaseModel(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True

class Grade(BaseModel):
    name = models.CharField(_('name'), max_length=15)
    description = models.CharField(_('description'), max_length=200)

    def __unicode__(self):
        return self.name

class PhoneBook(BaseModel):
    name = models.CharField(_('name'), max_length=200)
    phone_number = models.CharField(_('Phone Number'), max_length=16, unique=True, db_index=True)

    class Meta:
        db_table = 'driji_phonebook'

    def __unicode__(self):
        return self.name

class PeopleBaseModel(BaseModel):
    name = models.CharField(_('name'), max_length=200)
    address = models.CharField(_('address'), max_length=200, blank=True, null=True)
    phonebook = models.ForeignKey(PhoneBook, blank=True, null=True)

    class Meta:
        abstract = True

class Parent(PeopleBaseModel):

    class Meta:
        db_table = 'driji_parent'

    def __unicode__(self):
        return self.name

class Student(PeopleBaseModel):
    attendance = models.ForeignKey(ZKUser, related_name='students', blank=True, null=True)
    grade = models.ForeignKey(Grade, related_name='students')

    class Meta:
        db_table = 'driji_student'

    def __unicode__(self):
        return self.name
