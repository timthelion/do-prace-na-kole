# -*- coding: utf-8 -*-
# Author: Timothy Hobbs <timothy <at> hobbs.cz>

from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _


class StravaAccount(models.Model):
    """Strava účet"""
    class Meta:
        verbose_name = _("Strava účet")
        verbose_name_plural = _("Strava účty")

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    access_token = models.CharField(
        max_length=64,
    )

    last_sync_time = models.DateTimeField(
        "Poslední synchronizace",
        null=True,
        default=None,
    )

    strava_username = models.CharField(
        max_length=64,
    )

    first_name = models.CharField(
        max_length=64,
    )

    last_name = models.CharField(
        max_length=64,
    )

    user_sync_count = models.IntegerField(
        default=0,
    )

    @classmethod
    def get_stale_accounts(cls, min_time_between_syncs=60 * 60 * 12):
        stale_cutoff = datetime.now() - min_time_between_syncs
        return cls.filter(last_sync_time__lte=stale_cutoff)
