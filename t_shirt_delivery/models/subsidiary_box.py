# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@email.cz>
#
# Copyright (C) 2017 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from django.contrib.gis.db import models
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from dpnk.models import UserAttendance

from model_utils.models import TimeStampedModel

from . import PackageTransaction
from .. import customer_sheets


class SubsidiaryBox(TimeStampedModel, models.Model):
    """ Krabice pro pobočku """

    class Meta:
        verbose_name = _("Krabice pro pobočku")
        verbose_name_plural = _("Krabice pro pobočky")

    delivery_batch = models.ForeignKey(
        'DeliveryBatch',
        verbose_name=_("Dávka objednávek"),
        null=False,
        blank=False,
    )
    customer_sheets = models.FileField(
        verbose_name=_(u"Zákaznické listy"),
        upload_to=u'customer_sheets',
        blank=True,
        null=True,
    )
    subsidiary = models.ForeignKey(
        'dpnk.Subsidiary',
        verbose_name=_("Pobočka"),
        null=True,
        blank=True,
    )
    dispatched = models.BooleanField(
        verbose_name=_("Vyřízeno"),
        blank=False,
        null=False,
        default=False,
    )

    def identifier(self):
        if self.id:
            return "S%s" % self.id

    def __str__(self):
        return _("Krabice pro pobočku %s") % self.subsidiary

    def get_representative_addressee(self):
        """ Returns UserAttendance to which this box should be addressed """
        if self.subsidiary and self.subsidiary.box_addressee_name:
            name = self.subsidiary.box_addressee_name
            email = self.subsidiary.box_addressee_email
            telephone = self.subsidiary.box_addressee_telephone
        else:
            user_attendance = UserAttendance.objects.filter(transactions__packagetransaction__team_package__box=self).first()
            name = user_attendance.userprofile.user.get_full_name() if user_attendance else ""
            email = user_attendance.userprofile.user.email if user_attendance else ""
            telephone = user_attendance.userprofile.telephone if user_attendance else ""
        return {
            'name': name,
            'email': email,
            'telephone': telephone,
        }

    def get_t_shirt_count(self):
        return PackageTransaction.objects.filter(team_package__box=self).count()

    def get_weight(self):
        """ Returns weight of this box """
        t_shirt_weight = self.delivery_batch.campaign.package_weight
        t_shirt_count = self.get_t_shirt_count()
        return t_shirt_weight * t_shirt_count

    def get_volume(self):
        campaign = self.delivery_batch.campaign
        t_shirt_volume = campaign.package_width * campaign.package_height * campaign.package_depth
        t_shirt_count = self.get_t_shirt_count()
        return t_shirt_volume * t_shirt_count

    def all_packages_dispatched(self):
        return not self.teampackage_set.filter(dispatched=False).exists()


@receiver(post_save, sender=SubsidiaryBox)
def create_customer_sheets(sender, instance, created, **kwargs):
    if not instance.customer_sheets and getattr(instance, 'add_packages_on_save', True):
        with NamedTemporaryFile() as temp:
            customer_sheets.make_customer_sheets_pdf(temp, instance)
            instance.customer_sheets.save("customer_sheets_%s_%s.pdf" % (instance.pk, instance.created.strftime("%Y-%m-%d")), File(temp))
            instance.save()