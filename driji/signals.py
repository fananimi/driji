# -*- coding: utf-8 -*-
from django.db import IntegrityError
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from driji.models import AttendanceSummary

from zkcluster.models import Attendance


@receiver(post_save, sender=Attendance)
def on_attendance_save(**kwargs):
    instance = kwargs['instance']
    try:
        AttendanceSummary.objects.create(
            zk_attendance=instance,
            date=instance.timestamp.date(),
            driji_user=instance.user
        )
    except IntegrityError:
        pass
