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
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory, Client
from django.test.utils import override_settings
from django_admin_smoke_tests import tests as smoke_tests
from dpnk import util, models, filters, actions
from dpnk.models import UserAttendance, Team, DeliveryBatch
from dpnk.test.util import DenormMixin
from dpnk.test.util import print_response  # noqa
import datetime
import settings


@override_settings(
    SITE_ID=2,
    FAKE_DATE=datetime.date(year=2010, month=11, day=20),
)
class AdminSmokeTests(DenormMixin, smoke_tests.AdminSiteSmokeTest):
    fixtures = ['campaign', 'auth_user', 'users', 'test_results_data', 'transactions', 'batches', 'invoices', 'trips']
    exclude_apps = ['djcelery']

    def setUp(self):
        super().setUp()
        util.rebuild_denorm_models(models.Team.objects.filter(pk__in=[4, 3, 1]))

    def get_request(self):
        request = super().get_request()
        request.subdomain = "testing-campaign"
        return request


@override_settings(
    SITE_ID=2,
    FAKE_DATE=datetime.date(year=2010, month=11, day=20),
)
class AdminModulesTests(DenormMixin, TestCase):
    fixtures = ['campaign', 'auth_user', 'users', 'transactions', 'batches', 'invoices']

    def setUp(self):
        super().setUp()
        self.client = Client(HTTP_HOST="testing-campaign.testserver", HTTP_REFERER="test-referer")
        self.client.force_login(User.objects.get(username='admin'), settings.AUTHENTICATION_BACKENDS[0])
        util.rebuild_denorm_models(Team.objects.filter(pk=1))
        util.rebuild_denorm_models(UserAttendance.objects.filter(pk=1115))

    def test_userattendance_export(self):
        address = "/admin/dpnk/userattendance/export/"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        self.assertContains(
            response,
            '1015,testing-campaign,,1,Testing team 1,approved,,Testing city,cs,,'
            'Testing,User,test1,test2@test.cz,"Ulice 1, 111 11 Praha",Testing company,2015-11-12 18:18:40,,,,'
        )

    def test_packagetransaction_export(self):
        DeliveryBatch.objects.create(campaign_id=339)
        address = "/admin/dpnk/packagetransaction/export/"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        self.assertContains(response, "1,,1115,Testing User 1,,test@test.cz,")
        self.assertContains(response, ",Ulice 1,11111,Praha,Testing company,test@test.cz,Testing t-shirt size,1,11111117,")

    def test_company_export(self):
        address = "/admin/dpnk/company/export/"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        self.assertContains(response, "2,Testing company without admin,11111")

    def test_subsidiary_export(self):
        address = "/admin/dpnk/subsidiary/export/"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        self.assertContains(response, "1,1,1")

    def test_answer_export(self):
        address = "/admin/dpnk/answer/export/"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        self.assertContains(response, "5,Testing,User 1,Testing team 1,Ulice,1,,,11111,Praha,Testing company,Testing city,2,,,1,yes,Answer without attachment")

    def test_invoice_export(self):
        address = "/admin/dpnk/invoice/export/"
        post_data = {
            'file_format': 0,
        }
        response = self.client.post(address, post_data)
        self.assertContains(response, "0.0,0,Testing campaign,1,,11111,CZ1234567890,0,Ulice,1,,,11111,Praha")

    def test_deliverybatch_masschange(self):
        address = "/admin/dpnk/deliverybatch-masschange/1/"
        response = self.client.get(address)
        self.assertContains(response, 'Zákaznické listy:')

    def test_competition_masschange(self):
        address = "/admin/dpnk/competition-masschange/3,5/"
        response = self.client.get(address)
        self.assertContains(response, '<option value="338">Testing campaign - last year</option>')

    def test_subsidiary_masschange(self):
        address = "/admin/dpnk/subsidiary-masschange/1/"
        response = self.client.get(address)
        self.assertContains(response, 'id="id_address_street_number"')

    def test_admin_questions(self):
        address = reverse('admin_questions')
        response = self.client.get(address)
        self.assertContains(response, 'Testing campaign -')

    def test_admin_answers(self):
        address = "%s?question=2" % reverse('admin_answers')
        response = self.client.get(address)
        self.assertContains(response, '<a href="/admin/dpnk/answer/?question__competition__id__exact=4">Odpovědi k soutěži Dotazník</a>')
        self.assertContains(response, '<a href="%s/DSC00002.JPG" target="_blank">DSC00002.JPG</a>' % settings.MEDIA_URL)

    def test_admin_companyadmin(self):
        address = "%s?administrated_company__subsidiaries__city__id__exact=1" % reverse('admin:dpnk_companyadmin_changelist')
        response = self.client.get(address)
        self.assertContains(response, 'test_wa@email.cz')
        self.assertContains(response, 'Null User')

    def test_admin_companyadmin_admin_approved_filter(self):
        address = "%s?company_admin_approved__exact=approved" % reverse('admin:dpnk_companyadmin_changelist')
        response = self.client.get(address)
        self.assertContains(response, 'test_wa@email.cz')
        self.assertContains(response, 'Null User')

    def test_admin_userprofile(self):
        address = "%s?userattendance_set__team__subsidiary__city__id__exact=1" % reverse('admin:dpnk_userprofile_changelist')
        response = self.client.get(address)
        self.assertContains(response, 'email1031@dopracenakole.cz')
        self.assertContains(response, 'Registered User 1')

    def test_admin_userprofile_sex_filter(self):
        address = "%s?sex__exact=male" % reverse('admin:dpnk_userprofile_changelist')
        response = self.client.get(address)
        self.assertContains(response, 'email1031@dopracenakole.cz')
        self.assertContains(response, 'Registered User 1')


@override_settings(
    SITE_ID=2,
    FAKE_DATE=datetime.date(year=2010, month=11, day=20),
)
class BatchAdminTests(TestCase):
    fixtures = ['campaign', 'auth_user', 'users', 'test_results_data', 'transactions', 'trips']

    def setUp(self):
        self.client = Client(HTTP_HOST="testing-campaign.testserver")
        self.client.force_login(User.objects.get(username='admin'), settings.AUTHENTICATION_BACKENDS[0])

    def test_userattendancetobatch_admin(self):
        address = reverse('admin:dpnk_userattendancetobatch_changelist')
        response = self.client.get(address, follow=True)
        self.assertContains(response, "Ulice 1, 111 11 Praha - Testing city")
        self.assertContains(response, "1 Uživatel na dávku objednávek")
        self.assertContains(response, "field-payment_created")


@override_settings(
    SITE_ID=2,
    FAKE_DATE=datetime.date(year=2010, month=11, day=20),
)
class AdminTests(TestCase):
    fixtures = ['campaign', 'auth_user', 'users', 'test_results_data', 'transactions', 'batches', 'invoices', 'trips']

    def setUp(self):
        self.client = Client(HTTP_HOST="testing-campaign.testserver")
        self.client.force_login(User.objects.get(username='admin'), settings.AUTHENTICATION_BACKENDS[0])
        util.rebuild_denorm_models(Team.objects.filter(pk=1))
        self.user_attendance = UserAttendance.objects.filter(pk=1115)
        util.rebuild_denorm_models(self.user_attendance)

    def test_subsidiary_admin(self):
        address = reverse('admin:dpnk_subsidiary_changelist')
        response = self.client.get(address, follow=True)
        self.assertContains(response, "Ulice 1, 111 11 Praha - Testing city")

    def test_competition_admin(self):
        address = reverse('admin:dpnk_competition_changelist')
        response = self.client.get(address, follow=True)
        self.assertContains(response, "Pravidelnost")
        self.assertContains(response, "Výkonnost")

    def test_user_admin(self):
        address = reverse('admin:auth_user_changelist')
        response = self.client.get(address, follow=True)
        self.assertContains(response, "user_without_attendance")
        self.assertContains(response, "unapproved_user")

    def test_user_admin_change(self):
        address = reverse('admin:auth_user_change', args=(1128,))
        response = self.client.get(address, follow=True)
        self.assertContains(response, "Testing")
        self.assertContains(response, "User 1")

    def test_deliverybatch_admin(self):
        address = reverse('admin:dpnk_deliverybatch_changelist')
        response = self.client.get(address, follow=True)
        self.assertContains(response, "Testing campaign")
        self.assertContains(response, "field-customer_sheets__url")

    def test_deliverybatch_admin_change(self):
        models.PackageTransaction.objects.create(delivery_batch_id=1, t_shirt_size_id=1, user_attendance_id=1115)
        address = reverse('admin:dpnk_deliverybatch_change', args=(1,))
        response = self.client.get(address, follow=True)
        self.assertContains(response, "Testing t-shirt size: 2")
        self.assertContains(response, "Testing campaign")

    def test_admin_questionnaire_results(self):
        competition = models.Competition.objects.filter(slug="quest")
        actions.normalize_questionnqire_admissions(None, None, competition)
        competition.get().recalculate_results()
        address = reverse('admin_questionnaire_results', kwargs={'competition_slug': "quest"})
        response = self.client.get(address)
        self.assertContains(response, "Testing team 1 (Nick, Testing User 1, Registered User 1)")

    def test_admin_questionnaire_answers(self):
        competition = models.Competition.objects.filter(slug="quest")
        actions.normalize_questionnqire_admissions(None, None, competition)
        competition.get().recalculate_results()
        cr = models.CompetitionResult.objects.get(competition=competition)
        address = "%s?uid=%s" % (reverse('admin_questionnaire_answers', kwargs={'competition_slug': "quest"}), cr.id)
        response = self.client.get(address)
        self.assertContains(response, "%s/DSC00002.JPG" % settings.MEDIA_URL)
        self.assertContains(response, "Příloha:")
        self.assertContains(response, "Dohromady bodů: 16,2")

    def test_admin_questionnaire_answers_FB_LQ(self):
        competition = models.Competition.objects.filter(slug="FQ-LB")
        actions.normalize_questionnqire_admissions(None, None, competition)
        competition.get().recalculate_results()
        cr = models.CompetitionResult.objects.get(competition=competition)
        address = "%s?uid=%s" % (reverse('admin_questionnaire_answers', kwargs={'competition_slug': "FQ-LB"}), cr.id)
        response = self.client.get(address)
        self.assertContains(response, "Soutěžící: Testing team 1")
        self.assertContains(response, "Dohromady bodů: 0,0289855072463768")

    def test_admin_questionnaire_answers_dotaznik_spolecnosti(self):
        competition = models.Competition.objects.filter(slug="dotaznik-spolecnosti")
        actions.normalize_questionnqire_admissions(None, None, competition)
        competition.get().recalculate_results()
        cr = models.CompetitionResult.objects.get(competition=competition)
        address = "%s?uid=%s" % (reverse('admin_questionnaire_answers', kwargs={'competition_slug': "dotaznik-spolecnosti"}), cr.id)
        response = self.client.get(address)
        print_response(response)
        self.assertContains(response, "Soutěžící: Testing company")
        self.assertContains(response, "Dohromady bodů: 0,0")

    def test_admin_draw_results_fq_lb(self):
        models.Payment.objects.create(user_attendance_id=1015, status=models.Status.DONE, amount=1)
        models.Payment.objects.create(user_attendance_id=2115, status=models.Status.DONE, amount=1)
        util.rebuild_denorm_models(models.UserAttendance.objects.filter(id__in=[1015, 2115]))
        competition = models.Competition.objects.get(slug="FQ-LB")
        cr = models.CompetitionResult.objects.get(team_id=1, competition=competition)
        cr.result = 0.8
        cr.save()
        address = reverse('admin_draw_results', kwargs={'competition_slug': "FQ-LB"})
        response = self.client.get(address)
        self.assertContains(response, "1. tah: Tým Testing team 1 z organizace Testing company")

    def test_admin_draw_results_fq_lb_not_all_paying(self):
        competition = models.Competition.objects.get(slug="FQ-LB")
        cr = models.CompetitionResult.objects.get(team_id=1, competition=competition)
        cr.result = 0.8
        cr.save()
        address = reverse('admin_draw_results', kwargs={'competition_slug': "FQ-LB"})
        response = self.client.get(address)
        self.assertContains(response, "Tato soutěž nemá žádné týmy splňující kritéria")

    def test_admin_draw_results_vykonnost(self):
        competition = models.Competition.objects.filter(slug="vykonnost")
        competition.get().recalculate_results()
        address = reverse('admin_draw_results', kwargs={'competition_slug': "vykonnost"})
        response = self.client.get(address)
        self.assertContains(response, "1. tah: Tým Testing User 1")

    def test_admin_draw_results_quest(self):
        competition = models.Competition.objects.filter(slug="quest")
        actions.normalize_questionnqire_admissions(None, None, competition)
        competition.get().recalculate_results()
        address = reverse('admin_draw_results', kwargs={'competition_slug': "quest"})
        response = self.client.get(address)
        self.assertContains(response, "1. tah: Tým Testing User 1")

    def test_admin_draw_results_tf(self):
        competition = models.Competition.objects.filter(slug="TF")
        competition.get().recalculate_results()
        address = reverse('admin_draw_results', kwargs={'competition_slug': "TF"})
        response = self.client.get(address)
        self.assertContains(response, "Tato soutěž nemá žádné týmy splňující kritéria")


@override_settings(
    SITE_ID=2,
    FAKE_DATE=datetime.date(year=2010, month=11, day=20),
)
class LocalAdminTests(TestCase):
    fixtures = ['campaign', 'auth_user', 'users', 'test_results_data', 'transactions', 'batches', 'invoices', 'trips']

    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(pk=2), settings.AUTHENTICATION_BACKENDS[0])

    def test_competition_change_view_different_city(self):
        address = reverse('admin:dpnk_competition_change', args=(3,))
        response = self.client.get(address, follow=True)
        self.assertEquals(response.status_code, 404)

    def test_competition_change_view(self):
        address = reverse('admin:dpnk_competition_change', args=(6,))
        response = self.client.get(address, follow=True)
        self.assertContains(response, "Výkonnost ve městě")


class FilterTests(TestCase):
    fixtures = ['campaign', 'auth_user', 'users', 'invoices', 'trips']

    def setUp(self):
        self.factory = RequestFactory()
        self.user_attendance = UserAttendance.objects.get(pk=1115)
        self.session_id = "2075-1J1455206457"
        self.trans_id = "2055"
        models.Payment.objects.create(
            session_id=self.session_id,
            user_attendance=self.user_attendance,
            amount=150
        )
        self.request = self.factory.get("")
        self.request.subdomain = "testing-campaign"

    def test_email_filter_blank(self):
        f = filters.EmailFilter(self.request, {"email": "duplicate"}, User, None)
        q = f.queryset(self.request, User.objects.all())
        self.assertEquals(q.count(), 0)

    def test_email_filter_duplicate(self):
        f = filters.EmailFilter(self.request, {"email": "blank"}, User, None)
        q = f.queryset(self.request, User.objects.all())
        self.assertEquals(q.count(), 0)

    def test_email_filter_null(self):
        f = filters.EmailFilter(self.request, {}, User, None)
        q = f.queryset(self.request, User.objects.all())
        self.assertEquals(q.count(), 8)

    def test_has_team_filter_yes(self):
        f = filters.HasTeamFilter(self.request, {"user_has_team": "yes"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 6)

    def test_has_team_filter_no(self):
        f = filters.HasTeamFilter(self.request, {"user_has_team": "no"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 1)

    def test_has_team_filter_null(self):
        f = filters.HasTeamFilter(self.request, {}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 7)

    def test_is_for_company_yes(self):
        f = filters.IsForCompanyFilter(self.request, {"is_for_company": "yes"}, models.Competition, None)
        q = f.queryset(self.request, models.Competition.objects.all())
        self.assertEquals(q.count(), 2)

    def test_is_for_company_no(self):
        f = filters.IsForCompanyFilter(self.request, {"is_for_company": "no"}, models.Competition, None)
        q = f.queryset(self.request, models.Competition.objects.all())
        self.assertEquals(q.count(), 8)

    def test_is_for_company_null(self):
        f = filters.IsForCompanyFilter(self.request, {}, models.Competition, None)
        q = f.queryset(self.request, models.Competition.objects.all())
        self.assertEquals(q.count(), 10)

    def test_has_rides_filter_yes(self):
        f = filters.HasRidesFilter(self.request, {"has_rides": "yes"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 1)

    def test_has_rides_filter_no(self):
        f = filters.HasRidesFilter(self.request, {"has_rides": "no"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 6)

    def test_has_rides_filter_null(self):
        f = filters.HasRidesFilter(self.request, {}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 7)

    def test_has_voucher_filter_yes(self):
        f = filters.HasVoucherFilter(self.request, {"has_voucher": "yes"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 0)

    def test_has_voucher_filter_no(self):
        f = filters.HasVoucherFilter(self.request, {"has_voucher": "no"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 7)

    def test_has_voucher_filter_null(self):
        f = filters.HasVoucherFilter(self.request, {}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 7)

    def test_campaign_filter_campaign(self):
        f = filters.CampaignFilter(self.request, {"campaign": "testing-campaign"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 5)

    def test_campaign_filter_none(self):
        f = filters.CampaignFilter(self.request, {"campaign": "none"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 0)

    def test_campaign_filter_without_subdomain(self):
        self.request.subdomain = None
        f = filters.CampaignFilter(self.request, {"campaign": "none"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 0)

    def test_campaign_filter_unknown_campaign(self):
        self.request.subdomain = "asdf"
        f = filters.CampaignFilter(self.request, {}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 0)

    def test_campaign_filter_all(self):
        f = filters.CampaignFilter(self.request, {"campaign": "all"}, models.UserAttendance, None)
        q = f.queryset(self.request, models.UserAttendance.objects.all())
        self.assertEquals(q.count(), 7)

    def test_city_campaign_filter_all(self):
        f = filters.CityCampaignFilter(self.request, {"campaign": "all"}, models.City, None)
        q = f.queryset(self.request, models.City.objects.all())
        self.assertEquals(q.count(), 2)

    def test_invoice_paid_filters_yes(self):
        f = filters.InvoicePaidFilter(self.request, {"invoice_paid": "yes"}, models.Invoice, None)
        q = f.queryset(self.request, models.Invoice.objects.all())
        self.assertEquals(q.count(), 0)

    def test_invoice_paid_filters_no(self):
        f = filters.InvoicePaidFilter(self.request, {"invoice_paid": "no"}, models.Invoice, None)
        q = f.queryset(self.request, models.Invoice.objects.all())
        self.assertEquals(q.count(), 1)

    def test_invoice_paid_filters_null(self):
        f = filters.InvoicePaidFilter(self.request, {}, models.Invoice, None)
        q = f.queryset(self.request, models.Invoice.objects.all())
        self.assertEquals(q.count(), 1)

    def test_has_useratendance_filter_yes(self):
        f = filters.HasUserAttendanceFilter(self.request, {"has_user_attendance": "yes"}, models.CompanyAdmin, None)
        q = f.queryset(self.request, models.CompanyAdmin.objects.all())
        self.assertEquals(q.count(), 0)

    def test_has_useratendance_filter_no(self):
        f = filters.HasUserAttendanceFilter(self.request, {"has_user_attendance": "no"}, models.CompanyAdmin, None)
        q = f.queryset(self.request, models.CompanyAdmin.objects.all())
        self.assertEquals(q.count(), 3)

    def test_has_useratendance_filter_null(self):
        f = filters.HasUserAttendanceFilter(self.request, {}, models.CompanyAdmin, None)
        q = f.queryset(self.request, models.CompanyAdmin.objects.all())
        self.assertEquals(q.count(), 3)

    def test_has_reaction_filter_yes(self):
        f = filters.HasReactionFilter(self.request, {"has_reaction": "yes"}, models.Answer, None)
        q = f.queryset(self.request, models.Answer.objects.all())
        self.assertEquals(q.count(), 4)

    def test_has_reaction_filter_no(self):
        f = filters.HasReactionFilter(self.request, {"has_reaction": "no"}, models.Answer, None)
        q = f.queryset(self.request, models.Answer.objects.all())
        self.assertEquals(q.count(), 1)

    def test_has_reaction_filter_null(self):
        f = filters.HasReactionFilter(self.request, {}, models.Answer, None)
        q = f.queryset(self.request, models.Answer.objects.all())
        self.assertEquals(q.count(), 5)

    def test_has_userprofile_filter_yes(self):
        f = filters.HasUserprofileFilter(self.request, {"has_userprofile": "yes"}, User, None)
        q = f.queryset(self.request, User.objects.all())
        self.assertEquals(q.count(), 7)

    def test_has_userprofile_filter_no(self):
        f = filters.HasUserprofileFilter(self.request, {"has_userprofile": "no"}, User, None)
        q = f.queryset(self.request, User.objects.all())
        self.assertEquals(q.count(), 1)

    def test_has_userprofile_filter_null(self):
        f = filters.HasUserprofileFilter(self.request, {}, User, None)
        q = f.queryset(self.request, User.objects.all())
        self.assertEquals(q.count(), 8)

    def test_has_track_filter_yes(self):
        f = filters.TrackFilter(self.request, {"has_track": "yes"}, User, None)
        q = f.queryset(self.request, UserAttendance.objects.all())
        self.assertEquals(q.count(), 5)

    def test_has_track_filter_no(self):
        f = filters.TrackFilter(self.request, {"has_track": "no"}, User, None)
        q = f.queryset(self.request, UserAttendance.objects.all())
        self.assertEquals(q.count(), 2)

    def test_has_track_filter_null(self):
        f = filters.TrackFilter(self.request, {}, User, None)
        q = f.queryset(self.request, UserAttendance.objects.all())
        self.assertEquals(q.count(), 7)
