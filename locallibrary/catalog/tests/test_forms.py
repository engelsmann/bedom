import datetime

from django.test import TestCase
from django.utils import timezone

from catalog.forms import RenewBookForm

##  Note (https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing#note_11)
##  Here we don't actually use the database or test client. Consider modifying these tests to use SimpleTestCase. https://docs.djangoproject.com/en/3.1/topics/testing/tools/#django.test.SimpleTestCase
##  We also need to validate that the correct errors are raised if the form is invalid, however this is usually done as part of view processing, so we'll take care of that in the next section.



class RenewBookFormTest(TestCase):
    def test_renew_form_date_field_label(self):
        form = RenewBookForm()
        # self.assertTrue(form.fields['due_back'].label is None or form.fields['due_back'].label == 'due back')

        ## Changed label in .forms.RenewBookForm.Meta
        self.assertEquals(form.fields['due_back'].label, 'Renewal date')

    def test_renew_form_date_field_help_text(self):
        form = RenewBookForm()
        self.assertEqual(form.fields['due_back'].help_text, 'Enter a date between now and 4 weeks (default 3).')

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewBookForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form = RenewBookForm(data={'due_back': date})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4)
        form = RenewBookForm(data={'due_back': date})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_after_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewBookForm(data={'due_back': date})
        self.assertFalse(form.is_valid())
