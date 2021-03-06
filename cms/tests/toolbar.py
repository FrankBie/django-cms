from __future__ import with_statement
from cms.api import create_page
from cms.test_utils.testcases import SettingsOverrideTestCase
from cms.test_utils.util.context_managers import (UserLoginContext, 
    SettingsOverride)
from django.conf import settings


class ToolbarTests(SettingsOverrideTestCase):
    settings_overrides = {'CMS_MODERATOR': False}
    
    def test_01_static_html(self):
        page = create_page("page", "nav_playground.html", "en", published=True)
        superuser = self.get_superuser()
        with SettingsOverride(DEBUG=True):
            with UserLoginContext(self, superuser):
                response = self.client.get('%sstatic.html?edit' % settings.MEDIA_URL)
                self.assertTemplateNotUsed(response, 'cms/toolbar/toolbar.html')
                response = self.client.get('%s?edit' % page.get_absolute_url())
                self.assertTemplateUsed(response, 'cms/toolbar/toolbar.html')
