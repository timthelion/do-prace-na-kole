# -*- coding: utf-8 -*-

# Author: Petr Dlouhý <petr.dlouhy@auto-mat.cz>
#
# Copyright (C) 2016 o.s. Auto*Mat
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
from django.contrib.gis.db.models.functions import Length

from secretballot.middleware import SecretBallotIpUseragentMiddleware

from .models import Campaign, UserAttendance


class UserAttendanceMiddleware:
    def process_request(self, request):
        campaign_slug = request.subdomain
        if request.user and request.user.is_authenticated():
            try:
                request.user_attendance = UserAttendance.objects.select_related(
                    'campaign',
                    'team__subsidiary__city',
                    't_shirt_size',
                    'userprofile__user',
                    'representative_payment',
                    'related_company_admin',
                ).annotate(
                    length=Length('track'),
                ).get(
                    userprofile__user=request.user,
                    campaign__slug=campaign_slug,
                )
                request.campaign = request.user_attendance.campaign
            except UserAttendance.DoesNotExist:
                request.user_attendance = None
        else:
            request.user_attendance = None

        try:
            request.campaign = Campaign.objects.get(slug=campaign_slug)
        except Campaign.DoesNotExist:
            request.campaign = None


class SecretBallotUserMiddleware(SecretBallotIpUseragentMiddleware):

    def generate_token(self, request):
        if request.user.is_authenticated():
            return request.user.username
        else:
            return None
