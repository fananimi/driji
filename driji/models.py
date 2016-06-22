from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from zkcluster.models import ZKBaseUser

class BaseModel(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        abstract = True

class Profile(BaseModel, ZKBaseUser):
    USER_ADMINISTRATOR = 1
    USER_STAFF = 2
    USER_PARENT = 3
    USER_STUDENT = 4

    USER_TYPE = (
        (USER_ADMINISTRATOR, _('Administrator')),
        (USER_STAFF, _('Staff / Teacher')),
        (USER_PARENT, _('Parent')),
        (USER_STUDENT, _('Student'))
    )

    GENDER_MALE = _('male')
    GENDER_FEMALE = _('female')

    GENDER_CHOICES = (
        ('m', GENDER_MALE),
        ('f', GENDER_FEMALE)
    )

    user = models.OneToOneField(User, related_name='profile', blank=True, null=True)
    fullname = models.CharField(_('full name'), max_length=100)
    user_type = models.IntegerField(choices=USER_TYPE, default=USER_STUDENT)
    gender = models.CharField(_('gender'), max_length=1, choices=GENDER_CHOICES, default='m')

    NAME_FIELD = 'fullname'

    class Meta:
        db_table = 'driji_profile'

    def __unicode__(self):
        return self.fullname

# class Grade(BaseModel):
#     name = models.CharField(_('name'), max_length=15)
#     description = models.CharField(_('description'), max_length=200, blank=True, null=True)
#     profiles = models.ManyToManyField(
#         profiles,
#         verbose_name=_('profiles'),
#         blank=True,
#         related_name="grade_set",
#         related_query_name="grade",
#     )
#
#     class Meta:
#         db_table = 'driji_grade'
#
#     def __unicode__(self):
#         return self.name

class PhoneBook(BaseModel):
    address = models.CharField(_('address'), max_length=200, blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=16, unique=True, db_index=True)
    profile = models.ForeignKey(Profile, related_name='ponebooks')

    class Meta:
        db_table = 'driji_phonebook'

    def __unicode__(self):
        return self.profile.fullname
