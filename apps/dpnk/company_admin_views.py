# -*- coding: utf-8 -*-
# Author: Petr Dlouhý <petr.dlouhy@email.cz>
#
# Copyright (C) 2013 o.s. Auto*Mat
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

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.http import Http404
import django.contrib.auth
from django.conf import settings
from django.views.generic.edit import UpdateView, FormView
from decorators import must_be_company_admin
from company_admin_forms import SelectUsersPayForm, CompanyForm, CompanyAdminApplicationForm, CompanyAdminForm, CompanyCompetitionForm
from dpnk.email import company_admin_register_competitor_mail, company_admin_register_no_competitor_mail
from wp_urls import wp_reverse
from util import redirect
from models import Company, CompanyAdmin, Payment, Competition, Campaign, UserProfile
import models
import registration.signals, registration.backends
import registration.backends.simple
import logging
logger = logging.getLogger(__name__)

@must_be_company_admin
@login_required
def company_structure(request,
        template = 'company_admin/structure.html',
        company_admin = None,
        ):
    return render_to_response(template,
                              {
                                'company': company_admin.administrated_company,
                                'campaign': company_admin.campaign,
                                }, context_instance=RequestContext(request))

class SelectUsersPayView(FormView):
    template_name = 'generic_form_template.html'
    form_class = SelectUsersPayForm
    success_url = 'company_admin'

    def get_initial(self):
        return {
                'company_admin': self.kwargs.get('company_admin'),
                }

    def form_valid(self, form):
        paing_for = form.cleaned_data['paing_for']
        for userprofile in paing_for:
            for payment in userprofile.payments().all():
                if payment.pay_type == 'fc':
                    payment.status = Payment.Status.COMPANY_ACCEPTS
                    payment.save()
                    break
        logger.info("Company admin %s is paing for following users: %s" % (self.request.user, map(lambda x: x, paing_for)))
        super(SelectUsersPayView, self).form_valid(form)
        return redirect(wp_reverse(self.success_url))

class CompanyEditView(UpdateView):
    template_name = 'generic_form_template.html'
    form_class = CompanyForm
    model = Company
    success_url = 'company_admin'

    def get_object(self, queryset=None):
        return self.kwargs.get('company_admin').administrated_company

    def form_valid(self, form):
        super(CompanyEditView, self).form_valid(form)
        return redirect(wp_reverse(self.success_url))

class CompanyAdminRegistrationBackend(registration.backends.simple.SimpleBackend):
    def register(self, request, **cleaned_data):
        new_user = super(CompanyAdminRegistrationBackend, self).register(request, **cleaned_data)

        new_user.first_name = cleaned_data['first_name']
        new_user.last_name = cleaned_data['last_name']
        new_user.save()

        admin = CompanyAdmin(
            motivation_company_admin = cleaned_data['motivation_company_admin'],
            administrated_company = cleaned_data['administrated_company'],
            campaign = cleaned_data['campaign'],
            user = new_user,
        )
        admin.save()

        userprofile = UserProfile(
            user = new_user,
            telephone = cleaned_data['telephone'],
        )
        userprofile.save()
        company_admin_register_no_competitor_mail(admin.user, cleaned_data['administrated_company'])
        return new_user

class CompanyAdminApplicationView(FormView):
    template_name = 'company_admin/registration.html'
    form_class = CompanyAdminApplicationForm
    model = CompanyAdmin
    success_url = 'company_admin'

    def get_initial(self):
        return {
                'campaign': Campaign.objects.get(slug=self.kwargs.get('campaign_slug')),
                }

    def form_valid(self, form, backend='dpnk.company_admin_views.CompanyAdminRegistrationBackend'):
        super(CompanyAdminApplicationView, self).form_valid(form)
        backend = registration.backends.get_backend(backend)
        new_user = backend.register(self.request, **form.cleaned_data)
        auth_user = django.contrib.auth.authenticate(
            username=self.request.POST['username'],
            password=self.request.POST['password1'])
        django.contrib.auth.login(self.request, auth_user)

        return redirect(wp_reverse(self.success_url))

class CompanyAdminView(UpdateView):
    template_name = 'generic_form_template.html'
    form_class = CompanyAdminForm
    model = CompanyAdmin
    success_url = 'profil'

    def get_object(self, queryset=None):
        user_attendance = self.kwargs.get('user_attendance')
        campaign = user_attendance.campaign
        try:
            company_admin = self.request.user.company_admin.get(campaign=campaign)
        except CompanyAdmin.DoesNotExist:
            company_admin = CompanyAdmin(user=self.request.user, campaign=campaign)
        company_admin.administrated_company = user_attendance.team.subsidiary.company
        return company_admin

    def form_valid(self, form):
        super(CompanyAdminView, self).form_valid(form)
        company_admin_register_competitor_mail(self.kwargs.get('user_attendance'))
        return redirect(wp_reverse(self.success_url))

class CompanyCompetitionView(UpdateView):
    template_name = 'generic_form_template.html'
    form_class = CompanyCompetitionForm
    model = Competition
    success_url = 'company_admin'

    def __init__(self, *args, **kwargs):
        ret_val = super(CompanyCompetitionView, self).__init__(*args, **kwargs)
        return ret_val

    def get_object(self, queryset=None):
        company = self.kwargs.get('company_admin').administrated_company
        competition_slug = self.kwargs.get('competition_slug', None)
        campaign = self.kwargs.get('company_admin').campaign
        if competition_slug:
            competition = get_object_or_404(Competition.objects, slug = competition_slug)
            if competition.company != company:
                raise Http404(_(u"<div class='text-warning'>K editování této soutěže nemáte oprávnění.</div>"))
        else:
            if Competition.objects.filter(company=company, campaign=campaign).count() >= settings.MAX_COMPETITIONS_PER_COMPANY:
                raise Http404(_(u"<div class='text-warning'>Překročen maximální počet soutěží.</div>"))
            phase = campaign.phase_set.get(type='competition')
            competition = Competition(company=company, campaign=campaign, date_from=phase.date_from, date_to=phase.date_to )
        return competition


    def form_valid(self, form):
        super(CompanyCompetitionView, self).form_valid(form)
        return redirect(wp_reverse(self.success_url))

@must_be_company_admin
@login_required
def competitions(request,
        template = 'company_admin/competitions.html',
        company_admin = None,
        ):
    return render_to_response(template,
                              {
                                'competitions': company_admin.administrated_company.competition_set.all(),
                                }, context_instance=RequestContext(request))
