"""
Tests for the analytical.utils module.
"""

from django.conf import settings
from django.http import HttpRequest
from django.template import Context
from django.test.utils import override_settings

from analytical.utils import (
    get_domain, is_internal_ip, get_required_setting, AnalyticalException)
from analytical.tests.utils import TestCase


class SettingDeletedTestCase(TestCase):

    @override_settings(USER_ID=None)
    def test_get_required_setting(self):
        """
        Make sure using get_required_setting fails in the right place.
        """

        # available in python >= 3.2
        if hasattr(self, 'assertRaisesRegex'):
            with self.assertRaisesRegex(AnalyticalException, "^USER_ID setting is set to None$"):
                user_id = get_required_setting("USER_ID", "\d+", "invalid USER_ID")
        # available in python >= 2.7, deprecated in 3.2
        elif hasattr(self, 'assertRaisesRegexp'):
            with self.assertRaisesRegexp(AnalyticalException, "^USER_ID setting is set to None$"):
                user_id = get_required_setting("USER_ID", "\d+", "invalid USER_ID")
        else:
            self.assertRaises(AnalyticalException,
                              get_required_setting, "USER_ID", "\d+", "invalid USER_ID")

@override_settings(ANALYTICAL_DOMAIN="example.org")
class GetDomainTestCase(TestCase):
    def test_get_service_domain_from_context(self):
        context = Context({'test_domain': 'example.com'})
        self.assertEqual(get_domain(context, 'test'), 'example.com')

    def test_get_analytical_domain_from_context(self):
        context = Context({'analytical_domain': 'example.com'})
        self.assertEqual(get_domain(context, 'test'), 'example.com')

    @override_settings(TEST_DOMAIN="example.net")
    def test_get_service_domain_from_settings(self):
        context = Context()
        self.assertEqual(get_domain(context, 'test'), 'example.net')

    def test_get_analytical_domain_from_settings(self):
        context = Context()
        self.assertEqual(get_domain(context, 'test'), 'example.org')


# FIXME: enable Django apps dynamically and enable test again
#@with_apps('django.contrib.sites')
#@override_settings(TEST_DOMAIN=SETTING_DELETED,
#        ANALYTICAL_DOMAIN=SETTING_DELETED)
#class GetDomainTestCaseWithSites(TestCase):
#    def test_get_domain_from_site(self):
#        site = Site.objects.create(domain="example.com", name="test")
#        with override_settings(SITE_ID=site.id):
#            context = Context()
#            self.assertEqual(get_domain(context, 'test'), 'example.com')


class InternalIpTestCase(TestCase):

    @override_settings(ANALYTICAL_INTERNAL_IPS=['1.1.1.1'])
    def test_render_no_internal_ip(self):
        context = Context()
        self.assertFalse(is_internal_ip(context))

    @override_settings(ANALYTICAL_INTERNAL_IPS=['1.1.1.1'])
    def test_render_internal_ip(self):
        req = HttpRequest()
        req.META['REMOTE_ADDR'] = '1.1.1.1'
        context = Context({'request': req})
        self.assertTrue(is_internal_ip(context))

    @override_settings(TEST_INTERNAL_IPS=['1.1.1.1'])
    def test_render_prefix_internal_ip(self):
        req = HttpRequest()
        req.META['REMOTE_ADDR'] = '1.1.1.1'
        context = Context({'request': req})
        self.assertTrue(is_internal_ip(context, 'TEST'))

    @override_settings(INTERNAL_IPS=['1.1.1.1'])
    def test_render_internal_ip_fallback(self):
        req = HttpRequest()
        req.META['REMOTE_ADDR'] = '1.1.1.1'
        context = Context({'request': req})
        self.assertTrue(is_internal_ip(context))

    @override_settings(ANALYTICAL_INTERNAL_IPS=['1.1.1.1'])
    def test_render_internal_ip_forwarded_for(self):
        req = HttpRequest()
        req.META['HTTP_X_FORWARDED_FOR'] = '1.1.1.1'
        context = Context({'request': req})
        self.assertTrue(is_internal_ip(context))

    @override_settings(ANALYTICAL_INTERNAL_IPS=['1.1.1.1'])
    def test_render_different_internal_ip(self):
        req = HttpRequest()
        req.META['REMOTE_ADDR'] = '2.2.2.2'
        context = Context({'request': req})
        self.assertFalse(is_internal_ip(context))
