from django.db import models
from django.contrib.auth.models import User as AuthUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from zkcluster.models import ZKBaseUser, Attendance

class BaseModel(models.Model):
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        abstract = True

class User(BaseModel, ZKBaseUser):
    USER_ADMINISTRATOR = 1
    USER_STAFF = 2
    USER_PARENT = 3
    USER_STUDENT = 4

    USER_TYPE_CHOICES = (
        (USER_ADMINISTRATOR, _('Administrator')),
        (USER_STAFF, _('Staff / Teacher')),
        (USER_PARENT, _('Parent')),
        (USER_STUDENT, _('Student'))
    )

    GENDER_MALE = 'm'
    GENDER_FEMALE = 'f'

    GENDER_CHOICES = (
        (GENDER_MALE, _('male')),
        (GENDER_FEMALE, _('female'))
    )

    auth = models.OneToOneField(AuthUser, related_name='driji_user', blank=True, null=True)
    fullname = models.CharField(_('full name'), max_length=100)
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=USER_STUDENT)
    gender = models.CharField(_('gender'), max_length=1, choices=GENDER_CHOICES, default=GENDER_MALE)
    parent = models.ForeignKey("self", blank=True, null=True)

    NAME_FIELD = 'fullname'

    class Meta:
        db_table = 'driji_user'

    @property
    def gender_name(self):
        if self.gender == self.GENDER_MALE:
            return _('male')
        elif self.gender == self.GENDER_FEMALE:
            return _('female')

    def __unicode__(self):
        return self.fullname


class PhoneBook(BaseModel):
    address = models.CharField(_('address'), max_length=200, blank=True, null=True)
    phone_number = models.CharField(_('phone number'), max_length=16, unique=True, db_index=True)
    driji_user = models.ForeignKey(User, related_name='ponebooks')

    class Meta:
        db_table = 'driji_phonebook'

    def __unicode__(self):
        return self.driji_user.fullname

class AttendanceSummary(BaseModel):
    STATUS_PRESENT = 'p'
    STATUS_ABSENCE = 'a'
    STATUS_LATE = 'l'

    STATUS_CHOICES = (
        (STATUS_PRESENT, _('present')),
        (STATUS_ABSENCE, _('absense')),
        (STATUS_LATE, _('late'))
    )

    driji_user = models.ForeignKey(User, related_name='attendances')
    zk_attendance = models.OneToOneField(Attendance, related_name='summary')
    date = models.DateField()
    status = models.CharField(_('status'), max_length=1, choices=STATUS_CHOICES)

    def save(self, *args, **kwargs):
        timestamp = self.zk_attendance.timestamp
        late_time = timestamp.replace(hour=8, minute=0, microsecond=0)
        if  timestamp >= late_time:
            self.status = self.STATUS_LATE
        else:
            self.status = self.STATUS_PRESENT
        super(AttendanceSummary, self).save(*args, **kwargs)

    class Meta:
        db_table = 'driji_attendance_summary'
        unique_together = ('driji_user', 'date')
