"""
NOTE: For forms with fields gotten from any other models(foreign key field(s) in present models), use "TestCase" as you
would be creating an object of those model fields to pass the data to the present form field. Use SimpleTestCase for
forms without dependency.
"""

import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from django.test import SimpleTestCase, TestCase
from catalog.forms import LibrarianRenewBookModelForm, LibrarianApproveBookCopyBorrowModelForm, \
    LibrarianCreateBookCopyModelForm, LibrarianMarkBookCopyAsReturnedModelForm, LibrarianUpdateBookCopyModelForm, \
    UserBorrowBookModelForm, SignupForm
from catalog.models import Book


class LibrarianRenewBookModelFormTest(SimpleTestCase):
    def test_librarian_renew_form_due_back_label_is_renewal_date(self):
        form = LibrarianRenewBookModelForm()
        # Testing for None here because Django will return None if
        # the value is not explicitly set
        self.assertTrue(
            form.fields['due_back'].label is None or
            form.fields['due_back'].label == 'Renewal date'
        )

    def test_librarian_renew_form_renewal_date_help_text(self):
        form = LibrarianRenewBookModelForm()
        form_field_help_text = form.fields['due_back'].help_text
        self.assertEquals(form_field_help_text, "Enter a date between now and 2 weeks (default 1).")

    def test_librarian_renew_form_renewal_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = LibrarianRenewBookModelForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_librarian_renew_form_renewal_date_too_far_in_future(self):
        date = datetime.date.today() + datetime.timedelta(weeks=2) + datetime.timedelta(days=1)
        form = LibrarianRenewBookModelForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_librarian_renew_form_renewal_date_is_today(self):
        date = datetime.date.today()
        form = LibrarianRenewBookModelForm(data={'due_back': date})
        self.assertTrue(form.is_valid())

    def test_librarian_renew_form_renewal_max_date_of_two_weeks(self):
        date = timezone.localtime() + datetime.timedelta(weeks=2)
        form = LibrarianRenewBookModelForm(data={'due_back': date})
        self.assertTrue(form.is_valid())

    def test_librarian_renew_form_validation_error_for_renewal_date_in_the_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = LibrarianRenewBookModelForm(data={'due_back': date})
        form_error_message = ['Invalid date - renewal in past']
        self.assertEquals(form.errors, {'due_back': form_error_message})

    def test_librarian_renew_form_validation_error_for_renewal_date_above_two_weeks(self):
        date = datetime.date.today() + datetime.timedelta(weeks=2) + datetime.timedelta(days=1)
        form = LibrarianRenewBookModelForm(data={'due_back': date})
        error_message = ['Invalid date - renewal more than 2 weeks ahead']
        self.assertEquals(form.errors, {'due_back': error_message})

    def test_librarian_only_due_back_field_is_displayed(self):
        available_fields = ['due_back', ]
        form = LibrarianRenewBookModelForm()
        self.assertEquals(list(form.base_fields), available_fields)

    # def test_librarian_due_back_empty_input_error(self):
    #     form = LibrarianRenewBookModelForm(data={'due_back': None})
    #     self.assertFalse(form.is_valid())
    #     self.assertTrue('due_back') in form.errors # show that field due_back is the cause for this error


class UserBorrowBookModelFormTest(SimpleTestCase):
    def test_user_borrow_form_due_back_label_is_return_date(self):
        form = UserBorrowBookModelForm()
        self.assertTrue(
            form.fields['due_back'].label is None or
            form.fields['due_back'].label == 'Return date'
        )

    def test_user_borrow_form_return_date_help_text(self):
        form = UserBorrowBookModelForm()
        form_field_help_text = form.fields['due_back'].help_text
        self.assertEquals(form_field_help_text,
                          "Enter a proposed return date between now and 3 weeks (default 2).")

    def test_user_borrow_form_return_date_in_the_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = UserBorrowBookModelForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_user_borrow_form_return_date_more_than_three_weeeks(self):
        date = datetime.date.today() + datetime.timedelta(weeks=3) + datetime.timedelta(days=1)
        form = UserBorrowBookModelForm(data={'due_back': date})
        self.assertFalse(form.is_valid())

    def test_user_borrow_form_return_date_is_today(self):
        date = datetime.date.today()
        form = UserBorrowBookModelForm(data={'due_back': date})
        self.assertTrue(form.is_valid())

    def test_user_borrow_form_return_date_is_three_weeks_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=3)
        form = UserBorrowBookModelForm(data={'due_back': date})
        self.assertTrue(form.is_valid())

    def test_user_borrow_form_validation_error_return_date_in_the_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = UserBorrowBookModelForm(data={'due_back': date})
        form_error_message = ['Invalid date - return date the in past']
        self.assertEquals(form.errors, {'due_back': form_error_message})

    def test_user_borrow_form_validation_error_return_date_exceeds_three_weeks(self):
        form_date = {'due_back': datetime.date.today() + datetime.timedelta(weeks=3) + datetime.timedelta(days=1)}
        form = UserBorrowBookModelForm(data=form_date)
        form_error_message = ['Invalid date - return date more than 3 weeks ahead']
        self.assertEquals(form.errors, {'due_back': form_error_message})


class LibrarianCreateBookCopyModelFormTest(TestCase):
    # def test_librarian_create_form_id_label(self):
    #     form = LibrarianCreateBookCopyModelForm()
    #     self.assertTrue(form.fields['id'].label is None or
    #                     form.fields['id'].label == 'Id'
    #                     )
    #
    # def test_librarian_create_form_id_field_is_not_filled_by_the_librarian(self):
    #     form = LibrarianCreateBookCopyModelForm()
    #     self.assertFalse(form.fields['id'].required)

    def test_librarian_create_form_displays_specified_fields(self):
        available_fields = ['book', 'imprint', 'status']
        form = LibrarianCreateBookCopyModelForm()
        self.assertEquals(list(form.base_fields), available_fields)

    def test_librarian_create_form_status_is_maintenance(self):
        book = Book.objects.create(title='Here we go again')
        form_data = {
            'status': 'm',
            'imprint': 'Here we go again',
            'book': book
        }
        form = LibrarianCreateBookCopyModelForm(data=form_data)
        form_error_message = ['You must update as "Available" only!']
        self.assertEquals(form.errors, {'status': form_error_message})
        self.assertFalse(form.is_valid())

    def test_librarian_create_form_status_is_reserved(self):
        book = Book.objects.create(title='Here we go again')
        form_data = {
            'status': 'r',
            'imprint': 'Here we go again',
            'book': book
        }
        form = LibrarianCreateBookCopyModelForm(data=form_data)
        form_error_message = ['You must update as "Available" only!']
        self.assertEquals(form.errors, {'status': form_error_message})
        self.assertFalse(form.is_valid())

    def test_librarian_create_form_status_is_on_loan(self):
        book = Book.objects.create(title='Here we go again')
        form_data = {
            'status': 'o',
            'imprint': 'Here we go again',
            'book': book
        }
        form = LibrarianCreateBookCopyModelForm(data=form_data)
        form_error_message = ['You must update as "Available" only!']
        self.assertEquals(form.errors, {'status': form_error_message})
        self.assertFalse(form.is_valid())

    def test_librarian_create_form_status_is_available(self):
        book = Book.objects.create(title='Here we go again')
        form_data = {
            'status': 'a',
            'imprint': 'Here we go again',
            'book': book
        }
        form = LibrarianCreateBookCopyModelForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_librarian_create_form_book_label_is_book(self):
        form = LibrarianCreateBookCopyModelForm()
        self.assertTrue(
            form.fields['book'].label is None or
            form.fields['book'].label == 'Book'
        )

    def test_librarian_create_form_imprint_label_is_imprint(self):
        form = LibrarianCreateBookCopyModelForm()
        self.assertTrue(
            form.fields['imprint'].label is None or
            form.fields['imprint'].label == 'Imprint'
        )

    def test_librarian_create_form_status_label_is_status(self):
        form = LibrarianCreateBookCopyModelForm()
        self.assertTrue(
            form.fields['status'].label is None or
            form.fields['status'].label == 'Status'
        )


class LibrarianApproveBookCopyBorrowModelFormTest(SimpleTestCase):
    def test_librarian_book_copy_borrow_form_due_back_label_is_return_date(self):
        form = LibrarianApproveBookCopyBorrowModelForm()
        self.assertTrue(
            form.fields['status'].label is None or
            form.fields['status'].label == 'Status'
        )

    def test_librarian_book_copy_form_displays_specified_fields(self):
        available_fields = ['status', ]
        form = LibrarianApproveBookCopyBorrowModelForm()
        self.assertEquals(list(form.base_fields), available_fields)

    def test_librarian_book_copy_borrow_form_validation_error_on_status_maintenance(self):
        form_status = {'status': 'm'}
        form = LibrarianApproveBookCopyBorrowModelForm(data=form_status)
        form_error_message = ['You must approve as "On-Loan" ']
        self.assertEquals(form.errors, {'status': form_error_message})
        self.assertFalse(form.is_valid())

    def test_librarian_book_copy_borrow_form_validation_error_on_status_reserved(self):
        form_status = {'status': 'r'}
        form = LibrarianApproveBookCopyBorrowModelForm(data=form_status)
        form_error_message = ['You must approve as "On-Loan" ']
        self.assertEquals(form.errors, {'status': form_error_message})
        self.assertFalse(form.is_valid())

    def test_librarian_book_copy_borrow_form_validation_error_on_status_available(self):
        form_status = {'status': 'a'}
        form = LibrarianApproveBookCopyBorrowModelForm(data=form_status)
        form_error_message = ['You must approve as "On-Loan" ']
        self.assertEquals(form.errors, {'status': form_error_message})
        self.assertFalse(form.is_valid())

    def test_librarian_book_copy_borrow_form_validation_error_on_status_on_loan(self):
        form_status = {'status': 'o'}
        form = LibrarianApproveBookCopyBorrowModelForm(data=form_status)
        self.assertTrue(form.is_valid())


class LibrarianUpdateBookCopyModelFormTest(SimpleTestCase):
    def test_librarian_update_book_copy_form_displays_specified_fields(self):
        available_fields = ['imprint', 'status']
        form = LibrarianUpdateBookCopyModelForm()
        self.assertEquals(list(form.base_fields), available_fields)

    def test_librarian_update_book_copy_form_status_is_on_loan(self):
        form_data = {
            'status': 'o',
            'imprint': 'Here not go',
        }
        form = LibrarianUpdateBookCopyModelForm(data=form_data)
        form_error_message = ['You must update as "Available" or "Maintenance" or "Reserved" only!']
        self.assertEquals(form.errors, {'status': form_error_message})
        self.assertFalse(form.is_valid())

    def test_librarian_update_book_copy_form_status_is_on_maintenance(self):
        form_data = {
            'status': 'm',
            'imprint': 'Here we go again',
        }
        form = LibrarianUpdateBookCopyModelForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_librarian_update_book_copy_form_status_is_on_available(self):
        form_data = {
            'status': 'a',
            'imprint': 'Here we go again',
        }
        form = LibrarianUpdateBookCopyModelForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_librarian_update_book_copy_form_status_is_on_reserve(self):
        form_data = {
            'status': 'r',
            'imprint': 'Here we go again',
        }
        form = LibrarianUpdateBookCopyModelForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_librarian_create_form_imprint_label_is_imprint(self):
        form = LibrarianUpdateBookCopyModelForm()
        self.assertTrue(
            form.fields['imprint'].label is None or
            form.fields['imprint'].label == 'Imprint'
        )

    def test_librarian_create_form_status_label_is_status(self):
        form = LibrarianUpdateBookCopyModelForm()
        self.assertTrue(
            form.fields['status'].label is None or
            form.fields['status'].label == 'Status'
        )


class LibrarianMarkBookCopyAsReturnedModelFormTest(TestCase):
    def test_librarian_mark_book_copy_as_return_form_displays_specified_fields(self):
        available_fields = ['borrower', 'due_back', 'status']
        form = LibrarianMarkBookCopyAsReturnedModelForm()
        self.assertEquals(list(form.base_fields), available_fields)

    def test_librarian_mark_book_copy_as_return_form_all_field_filled_with_invalid_values(self):
        borrower = User.objects.create(first_name='Mike', last_name='Ele')
        date = datetime.date.today() + datetime.timedelta(weeks=1)
        form_data = {
            'borrower': borrower,
            'due_back': date,
            'status': 'm',
        }
        form = LibrarianMarkBookCopyAsReturnedModelForm(data=form_data)
        form_error_message_status = ['You must mark as "Available" ']
        form_error_message_due_back = ['Date must be Null']
        form_error_message_borrower = ['Borrower field must be empty" ']
        self.assertEquals(form.errors, {
            'borrower': form_error_message_borrower,
            'due_back': form_error_message_due_back,
            'status': form_error_message_status
        })
        self.assertFalse(form.is_valid())

    def test_librarian_mark_book_copy_as_return_form_all_field_is_empty_with_valid_status(self):
        borrower = None
        date = None
        form_data = {
            'borrower': borrower,
            'due_back': date,
            'status': 'a',
        }
        form = LibrarianMarkBookCopyAsReturnedModelForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_librarian_mark_book_copy_as_return_form_all_field_is_empty_with_invalid_status(self):
        borrower = None
        date = None
        form_data = {
            'borrower': borrower,
            'due_back': date,
            'status': 'o',
        }
        form = LibrarianMarkBookCopyAsReturnedModelForm(data=form_data)
        form_error_message_status = ['You must mark as "Available" ']
        self.assertEquals(form.errors, {
            'status': form_error_message_status
        })
        self.assertFalse(form.is_valid())

    def test_librarian_mark_book_copy_as_return_form_with_status_only_valid(self):
        borrower = User.objects.create(first_name='Mike', last_name='Ele')
        date = datetime.date.today() + datetime.timedelta(weeks=1)
        form_data = {
            'borrower': borrower,
            'due_back': date,
            'status': 'a',
        }
        form = LibrarianMarkBookCopyAsReturnedModelForm(data=form_data)
        form_error_message_due_back = ['Date must be Null']
        form_error_message_borrower = ['Borrower field must be empty" ']
        self.assertEquals(form.errors, {
            'borrower': form_error_message_borrower,
            'due_back': form_error_message_due_back
        })
        self.assertFalse(form.is_valid())

    def test_librarian_mark_book_copy_as_return_form_borrower_label_is_borrower(self):
        form = LibrarianMarkBookCopyAsReturnedModelForm()
        self.assertTrue(
            form.fields['borrower'].label is None or
            form.fields['borrower'].label == 'Borrower'
        )

    def test_librarian_mark_book_copy_as_return_form_due_back_label_is_due_back(self):
        form = LibrarianMarkBookCopyAsReturnedModelForm()
        self.assertTrue(
            form.fields['due_back'].label is None or
            form.fields['due_back'].label == 'Due back'
        )

    def test_librarian_mark_book_copy_as_return_form_status_label_is_status(self):
        form = LibrarianMarkBookCopyAsReturnedModelForm()
        self.assertTrue(
            form.fields['status'].label is None or
            form.fields['status'].label == 'Status'
        )


class SignupFormTest(SimpleTestCase):
    def test_sign_up_form_displays_specified_fields(self):
        available_fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        form = SignupForm()
        self.assertEquals(list(form.base_fields), available_fields)

    def test_sign_up_form_form_first_name_label_is_first_name(self):
        form = SignupForm()
        self.assertTrue(
            form.fields['first_name'].label is None or
            form.fields['first_name'].label == 'First name'
        )

    def test_sign_up_form_form_last_name_label_is_last_name(self):
        form = SignupForm()
        self.assertTrue(
            form.fields['last_name'].label is None or
            form.fields['last_name'].label == 'Last name'
        )

    def test_sign_up_form_form_username_label_is_username(self):
        form = SignupForm()
        self.assertTrue(
            form.fields['username'].label is None or
            form.fields['username'].label == 'Username'
        )

    def test_sign_up_form_form_email_label_is_email(self):
        form = SignupForm()
        self.assertTrue(
            form.fields['email'].label is None or
            form.fields['email'].label == 'Email'
        )

    def test_sign_up_form_form_password_1_label_is_password(self):
        form = SignupForm()
        self.assertTrue(
            form.fields['password1'].label is None or
            form.fields['password1'].label == 'Password'
        )

    def test_sign_up_form_form_password_2_label_is_password_confirm(self):
        form = SignupForm()
        self.assertTrue(
            form.fields['password2'].label is None or
            form.fields['password2'].label == 'Password confirmation'
        )

    def test_email_field_help_text(self):
        form = SignupForm()
        form_field_help_text = form.fields['email'].help_text
        self.assertEquals(form_field_help_text,
                          'Enter a valid email address as it would be used for your account confirmation')

    def test_email_field_max_length(self):
        form = SignupForm()
        form_field_max_length = form.fields['email'].max_length
        self.assertEquals(form_field_max_length, 150)
