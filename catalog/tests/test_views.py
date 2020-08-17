"""
NOTE: Always dynamically generate your pk in setUp if you can, so that the whole test_views.py file would pass when
all classes are run together

Models with fields that are foreign dependencies that needed to be filled on createview or updateview success,
don't redirect in unittest, but redirects in the browser as expected, why??? e.g bookinstance_create, book_create
book_update
"""

import datetime
import uuid

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.models import Author, Genre, Language, Book, BookInstance


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        NUMBER_OF_AUTHORS = 13

        for author_id in range(NUMBER_OF_AUTHORS):
            Author.objects.create(first_name='Rachel {}'.format(author_id),
                                  last_name='Abu {}'.format(author_id)
                                  )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEquals(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('catalog:author-list'))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_templates(self):
        response = self.client.get(reverse('catalog:author-list'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_nine(self):
        response = self.client.get(reverse('catalog:author-list'))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['author_list']) == 9)

    def test_list_all_authors(self):
        # Get second page and confirm it has exactly remaining 4 items
        response = self.client.get(reverse('catalog:author-list') + '?page=2')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['author_list']) == 4)


class AuthorDetailViewTest(TestCase):
    def setUp(self):
        author = Author.objects.create(first_name='Rachel', last_name='Abu')
        author.save()

        self.author = Author.objects.get(id=author.pk)

    def test_author_detail_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('catalog:author-detail', kwargs={'pk': self.author.id}))
        self.assertEquals(response.status_code, 200)

    def test_author_detail_does_not_exist(self):
        response = self.client.get('/catalog/authors/2/')
        self.assertEquals(response.status_code, 404)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('catalog:author-detail', kwargs={'pk': self.author.id}))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('catalog:author-detail', kwargs={'pk': self.author.id}))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_detail.html')


class AuthorCreateViewTest(TestCase):

    def setUp(self):
        self.librarian_user = User.objects.create(username="librarian_user", password='123456')
        self.normal_user = User.objects.create(username='normal_user', password='7890')
        self.librarian_user.save()
        self.normal_user.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user.user_permissions.add(permission)
        self.librarian_user.save()

    def test_user_with_permission_can_view_create_author(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:author_create'))
        self.assertEquals(response.status_code, 200)

    def test_user_with_permission_redirect_on_submit_of_author_create(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:author_create'))
        self.assertTemplateUsed(response, 'catalog/author_form.html')
        author_data = {'first_name': 'Rachel',
                       'last_name': 'Abu',
                       'date_of_birth': '1993-05-27'
                       }
        self.assertContains(response, 'first_name')
        self.assertContains(response, 'last_name')
        self.assertContains(response, 'date_of_birth')
        self.assertContains(response, 'date_of_death')
        new_response = self.client.post(reverse('catalog:author_create'), data=author_data)
        self.assertEquals(Author.objects.count(), 1)
        self.assertEquals(new_response.status_code, 302)
        # self.assertRedirects(new_response, reverse('catalog:author-detail', kwargs={'pk': 1}))

    def test_user_without_permission_cant_access_view(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/catalog/authors/create/')
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_author_create(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:author_create'))
        self.assertTemplateUsed(response, 'catalog/author_form.html')


class AuthorUpdateViewTest(TestCase):
    def setUp(self):
        test_author = Author.objects.create(first_name='Rachel', last_name='Abu', date_of_birth='1993-05-27')
        test_author.save()

        self.librarian_user1 = User.objects.create(username="librarian_user", password='12345')
        self.normal_user1 = User.objects.create(username='normal_user', password='78904')
        self.librarian_user1.save()
        self.normal_user1.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user1.user_permissions.add(permission)
        self.librarian_user1.save()

        self.author = Author.objects.get(id=test_author.pk)

    def test_user_with_permission_can_update_all_field(self):
        self.client.force_login(user=self.librarian_user1)
        response = self.client.get(reverse('catalog:author_update', kwargs={'pk': self.author.id}))
        self.assertTemplateUsed(response, 'catalog/author_form.html')

        # Check that the rendered view has original data from test_db
        self.assertEquals(self.author.first_name, 'Rachel')

        self.new_author_update = {'first_name': 'Monica',
                                  'last_name': 'Belucci',
                                  'date_of_birth': '1993-05-27',
                                  'date_of_death': '2100-12-25'
                                  }
        self.assertContains(response, 'first_name')
        self.assertContains(response, 'last_name')
        self.assertContains(response, 'date_of_birth')
        new_response = self.client.post(reverse('catalog:author_update', kwargs={'pk': self.author.id}),
                                        data=self.new_author_update)
        self.assertEquals(Author.objects.count(), 1)
        self.assertRedirects(new_response, reverse('catalog:author-detail', kwargs={'pk': self.author.id}))
        self.author.refresh_from_db()

        # Check that the original data has been updated to new data
        self.assertEquals(self.author.first_name, 'Monica')

    def test_user_with_permission_can_update_some_field(self):
        self.client.force_login(user=self.librarian_user1)
        response = self.client.get(reverse('catalog:author_update', kwargs={'pk': self.author.id}))
        self.assertTemplateUsed(response, 'catalog/author_form.html')
        self.assertEquals(self.author.last_name, 'Abu')
        self.new_author_update = {
            'first_name': 'Rachel',
            'last_name': 'Onojason',
            'date_of_birth': '1993-05-27',
            'date_of_death': '2103-12-31'
        }
        self.assertContains(response, 'first_name')
        self.assertContains(response, 'last_name')
        self.assertContains(response, 'date_of_birth')
        new_response = self.client.post(reverse('catalog:author_update', kwargs={'pk': self.author.id}),
                                        data=self.new_author_update)
        self.assertEquals(Author.objects.count(), 1)
        self.assertRedirects(new_response, reverse('catalog:author-detail', kwargs={'pk': self.author.id}))
        self.author.refresh_from_db()

        # Check that the original last_name data has been updated to the new data
        self.assertEquals(self.author.last_name, 'Onojason')

        # Check the first_name data still remained at it were originally
        self.assertEquals(self.author.first_name, 'Rachel')

    def test_user_without_permission_cant_view_author_update(self):
        self.client.force_login(user=self.normal_user1)
        response = self.client.get(reverse('catalog:author_update', kwargs={'pk': self.author.id}))
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_author_update(self):
        self.client.force_login(user=self.librarian_user1)
        response = self.client.get(reverse('catalog:author_update', kwargs={'pk': self.author.id}))
        self.assertTemplateUsed(response, 'catalog/author_form.html')


class AuthorDeleteViewTest(TestCase):
    def setUp(self):
        # Create 2 authors for deletion test
        NUMBER_OF_AUTHORS = 2

        for author_id in range(NUMBER_OF_AUTHORS):
            test_author = Author.objects.create(first_name='Moh {}'.format(author_id),
                                                last_name='Ella {}'.format(author_id)
                                                )

        self.author = Author.objects.get(id=test_author.pk)

        self.normal_user_1 = User.objects.create(username='normal', password='user')
        self.normal_user_1.save()

        self.librarian_user_1 = User.objects.create(username='librarian', password='useruser')
        self.librarian_user_1.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user_1.user_permissions.add(permission)
        self.librarian_user_1.save()

    def test_user_with_permission_can_view_author_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:author_delete', kwargs={'pk': self.author.id}))
        self.assertEquals(response.status_code, 200)

    def test_user_without_permission_cant_view_author_delete(self):
        self.client.force_login(user=self.normal_user_1)
        response = self.client.get(reverse('catalog:author_delete', kwargs={'pk': self.author.id}))
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_author_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:author_delete', kwargs={'pk': self.author.id}))
        self.assertTemplateUsed(response, 'catalog/author_confirm_delete.html')

    def test_author_deleted_successfully(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:author_delete', kwargs={'pk': self.author.id}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Are you sure you want to delete the author: {}?'.format(self.author))
        self.assertEquals(self.author.first_name, 'Moh 1')
        self.assertEquals(self.author.last_name, 'Ella 1')
        new_response = self.client.delete(reverse('catalog:author_delete', kwargs={'pk': self.author.id}))
        self.assertRedirects(new_response, reverse('catalog:author-list'))
        self.assertFalse(Author.objects.filter(id=self.author.id).exists())


class LoanedBookInstanceByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        self.test_user1 = User.objects.create(username='Joel', password='Onojason')
        self.test_user2 = User.objects.create(username='Rachel', password='Ene')

        self.test_user1.save()
        self.test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Obioma')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='23444789986',
            author=test_author,
            language=test_language,
        )

        # Create a genre as a post-step since it's a many-to-many field
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            the_borrower = self.test_user1 if book_copy % 2 else self.test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Joels publishing house',
                due_back=return_date,
                borrower=the_borrower,
                status=status
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('catalog:my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        self.client.force_login(user=self.test_user1)
        response = self.client.get(reverse('catalog:my-borrowed'))
        # Check that user is logged in
        self.assertEquals(str(response.context['user']), 'Joel')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/user_list_of_book_copies_borrowed.html')

    def test_only_borrowed_books_in_list(self):
        self.client.force_login(user=self.test_user2)
        response = self.client.get(reverse('catalog:my-borrowed'))
        self.assertEquals(response.status_code, 200)
        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEquals(len(response.context['bookinstance_list']), 0)
        self.assertContains(response, 'There are no books borrowed.')

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        # Because I used setUp(self), I am able to modify the objects of bookinstance to o from m
        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('catalog:my-borrowed'))
        self.assertEquals(str(response.context['user']), 'Rachel')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to Rachel are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEquals(response.context['user'], bookitem.borrower)
            self.assertEquals('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        # Change all book to be on loan
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        self.client.force_login(self.test_user1)
        response = self.client.get(reverse('catalog:my-borrowed'))
        self.assertEquals(str(response.context['user']), 'Joel')
        self.assertEquals(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEquals(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back

            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


class AllLoanedBooksLibrarianListViewTest(TestCase):
    def setUp(self):
        # Create three users with one user having permission
        self.test_user_1 = User.objects.create(username='Joel', password='Onojason')
        self.test_user_2 = User.objects.create(username='Rachel', password='Ene')
        self.librarian = User.objects.create(username='librarian_staff', password='users')

        self.test_user_1.save()
        self.test_user_2.save()
        self.librarian.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian.user_permissions.add(permission)
        self.librarian.save()

        # Create a book
        test_author = Author.objects.create(first_name='ken', last_name='Obioma')
        test_genre = Genre.objects.create(name='Thriller')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='23444789986',
            author=test_author,
            language=test_language,
        )

        # Create a genre as a post-step since it's a many-to-many field
        test_book.genre.set([test_genre, ])
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 31
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            the_borrower = self.test_user_1 if book_copy % 2 else self.test_user_2
            status = 'o'
            BookInstance.objects.create(
                book=test_book,
                imprint='Joels publishing house',
                due_back=return_date,
                borrower=the_borrower,
                status=status
            )

    def test_that_non_permitted_users_cant_access_this_view(self):
        self.client.force_login(user=self.test_user_1)
        response = self.client.get(reverse('catalog:all-borrowed'))
        self.assertEquals(response.status_code, 403)

    def test_that_users_with_permission_can_access_this_view(self):
        self.client.force_login(user=self.librarian)
        response = self.client.get(reverse('catalog:all-borrowed'))
        self.assertEquals(response.status_code, 200)

    def test_correct_template_used(self):
        self.client.force_login(user=self.librarian)
        response = self.client.get(reverse('catalog:all-borrowed'))
        self.assertTemplateUsed(response, 'catalog/librarian_all_book_copies_borrowed.html')

    def test_view_pagination(self):
        self.client.force_login(user=self.librarian)
        response = self.client.get(reverse('catalog:all-borrowed'))
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue('is_paginated' in response.context)
        self.assertEquals(str(response.context['user']), 'librarian_staff')
        self.assertEquals(len(response.context['bookinstance_list']), 10)

    def test_list_all_books_on_borrow(self):
        # Get third page and confirm it has exactly remaining 10 items
        self.client.force_login(user=self.librarian)
        response = self.client.get(reverse('catalog:all-borrowed') + '?page=3')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(len(response.context['bookinstance_list']) == 10)

    def test_only_borrowed_book_will_show_in_list(self):
        books = BookInstance.objects.all()
        for book_copy in books:
            book_copy.status = 'a'
            book_copy.save()

        self.client.force_login(user=self.librarian)
        response = self.client.get(reverse('catalog:all-borrowed'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['bookinstance_list']), 0)
        self.assertContains(response, 'There are no books borrowed.')

    def test_that_different_borrowers_on_list(self):
        user_1 = User.objects.get(username='Joel')
        user_2 = User.objects.get(username='Rachel')
        self.client.force_login(user=self.librarian)
        response = self.client.get(reverse('catalog:all-borrowed'))
        self.assertContains(response, 'All Borrowed Books')
        for bookitem in response.context['bookinstance_list']:
            if bookitem.borrower == user_1:
                self.assertEquals(str(bookitem.borrower), 'Joel')
                self.assertEquals('o', bookitem.status)
            elif bookitem.borrower == user_2:
                self.assertEquals(str(bookitem.borrower), 'Rachel')
                self.assertEquals('o', bookitem.status)

    def test_different_borrower_has_multiple_number_of_books_in_list(self):
        user_1 = User.objects.get(username='Joel')
        user_2 = User.objects.get(username='Rachel')
        self.client.force_login(self.librarian)
        response = self.client.get(reverse('catalog:all-borrowed'))
        self.assertEquals(response.status_code, 200)
        book_count_user_1 = BookInstance.objects.filter(status__exact='o').filter(borrower=user_1).count()
        self.assertEquals(book_count_user_1, 15)
        book_count_user_2 = BookInstance.objects.filter(status__exact='o').filter(borrower=user_2).count()
        self.assertEquals(book_count_user_2, 16)


class CopyOfBookAvailableViewTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create(username='testUser', password='123234')
        self.test_user.save()

        test_author = Author.objects.create(first_name='Jibola', last_name='G-Ballz')
        test_genre = Genre.objects.create(name='Romance')
        test_language = Language.objects.create(name='Yoruba')
        test_book = Book.objects.create(
            title='G-Ballz Thingz',
            summary='No summary for old men',
            isbn='234447892134',
            author=test_author,
            language=test_language,
        )

        # Create a genre as a post-step since it's a many-to-many field
        test_book.genre.set([test_genre, ])
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 31
        for book_copy in range(number_of_book_copies):
            status = ['a', 'm']
            BookInstance.objects.create(
                book=test_book,
                imprint='Abu publishing house',
                status=status[0] if book_copy % 2 else status[1]
            )

    def test_non_logged_in_user_cant_access_view(self):
        response = self.client.get(reverse('catalog:copy_available'))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/catalog/available/')

    def test_logged_in_user_can_access_view(self):
        self.client.force_login(user=self.test_user)
        response = self.client.get(reverse('catalog:copy_available'))
        self.assertEquals(response.status_code, 200)

    def test_correct_template_used(self):
        self.client.force_login(user=self.test_user)
        response = self.client.get(reverse('catalog:copy_available'))
        self.assertTemplateUsed(response, 'catalog/user_book_copies_available.html')

    def test_view_pagination(self):
        self.client.force_login(user=self.test_user)
        response = self.client.get(reverse('catalog:copy_available'))
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue('is_paginated' in response.context)
        self.assertEquals(str(response.context['user']), 'testUser')
        self.assertEquals(len(response.context['bookinstance_list']), 6)

    def test_view_list_all_available_books(self):
        self.client.force_login(user=self.test_user)
        # Get third page and confirm it has exactly remaining 3 items
        response = self.client.get(reverse('catalog:copy_available') + '?page=3')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['bookinstance_list']), 3)

    def test_only_available_books_are_displayed(self):
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('catalog:copy_available'))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Currently available books in the library')
        for book_item in response.context['bookinstance_list']:
            self.assertEquals(book_item.status, 'a')
        all_available_book_count = BookInstance.objects.filter(status__exact='a').count()
        self.assertEquals(all_available_book_count, 15)

    def test_no_copies_of_book_available(self):
        book = BookInstance.objects.all()
        for book_copy in book:
            book_copy.status = 'm'
            book_copy.save()
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('catalog:copy_available'))
        self.assertContains(response, 'There are no copies currently available to borrow in the library.')


class BorrowBooksRequestForLibrarianListViewTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create(username='User', password='12336')
        self.test_librarian = User.objects.create(username='Librarian', password='yuhghnjm')

        self.test_user.save()
        self.test_librarian.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.test_librarian.user_permissions.add(permission)
        self.test_librarian.save()

        author = Author.objects.create(first_name='Jibola', last_name='G-Ballz')
        genre_1 = Genre.objects.create(name='Romance')
        language = Language.objects.create(name='Yoruba')
        book = Book.objects.create(
            title='Semicolon',
            summary='Too tired for Summary',
            isbn='23444789223',
            author=author,
            language=language,
        )

        # Create a genre as a post-step since it's a many-to-many field
        book.genre.set([genre_1, ])
        book.save()

        # Create 31 BookInstance objects
        number_of_book_copies = 31
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            status = 'a'
            BookInstance.objects.create(
                book=book,
                imprint='Joels publishing house',
                due_back=return_date if book_copy % 2 else None,
                status=status
            )

    def test_user_without_permission_cant_access_view(self):
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('catalog:borrow_approval_list'))
        self.assertEquals(response.status_code, 403)

    def test_user_with_permission_can_access_view(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:borrow_approval_list'))
        self.assertEquals(response.status_code, 200)

    def test_correct_template_used_for_view(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:borrow_approval_list'))
        self.assertTemplateUsed(response, 'catalog/librarian_book_copy_borrow_approval_page.html')

    def test_pagination_for_view(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:borrow_approval_list'))
        self.assertTrue(response.context['is_paginated'])
        self.assertEquals(len(response.context['bookinstance_list']), 10)

    def test_list_all_book_copy_for_borrow_approval(self):
        self.client.force_login(self.test_librarian)
        # Only books with status available and due_back != null will be  displayed
        response = self.client.get(reverse('catalog:borrow_approval_list') + '?page=2')
        self.assertContains(response, 'Borrow Request')
        self.assertEquals(len(response.context['bookinstance_list']), 5)

    def test_only_available_book_with_due_back_date_is_displayed(self):
        book_to_display_count = BookInstance.objects.filter(status__exact='a').filter(due_back__isnull=False).count()
        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:borrow_approval_list'))
        self.assertTrue(response.context['bookinstance_list'])
        self.assertEquals(str(response.context['user']), 'Librarian')
        self.assertEquals(book_to_display_count, 15)

    def test_no_borrow_request(self):
        book = BookInstance.objects.all()
        for book_copy in book:
            book_copy.status = 'm'
            book_copy.save()

        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:borrow_approval_list'))
        self.assertContains(response, 'There are no borrow request currently.')


class CopyOfBookListViewTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create(username='User', password='12336')
        self.test_librarian = User.objects.create(username='Librarian', password='yuhghnjm')

        self.test_user.save()
        self.test_librarian.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.test_librarian.user_permissions.add(permission)
        self.test_librarian.save()

        author = Author.objects.create(first_name='Jibola', last_name='G-Ballz')
        genre_1 = Genre.objects.create(name='Romance')
        language = Language.objects.create(name='Yoruba')
        book = Book.objects.create(
            title='Semicolon',
            summary='Too tired for Summary',
            isbn='23444789223',
            author=author,
            language=language,
        )

        # Create a genre as a post-step since it's a many-to-many field
        book.genre.set([genre_1, ])
        book.save()

        # Create 31 BookInstance objects
        number_of_book_copies = 31
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            status = ['a', 'o']
            imprint = ['Abu Publishing House', 'Joels Publishing House']
            BookInstance.objects.create(
                book=book,
                imprint=imprint[0] if book_copy % 3 else imprint[1],
                due_back=return_date if status[1] else None,
                status=status[0] if book_copy % 3 else status[1]
            )

    def test_user_without_permission_cannot_access_view(self):
        self.client.force_login(self.test_user)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertEquals(response.status_code, 403)

    def test_user_with_permission_can_access_view(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(str(response.context['user']), 'Librarian')

    def test_pagination_for_view(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertTrue(response.context['is_paginated'])
        self.assertEquals(len(response.context['bookinstance_list']), 6)

    def test_pagination_for_last_page(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_list') + '?page=6')
        self.assertEquals(len(response.context['bookinstance_list']), 1)

    def test_correct_template_used(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertContains(response, 'Copies of Individual Books in the Library')
        self.assertTemplateUsed(response, 'catalog/bookinstance_list.html')

    def test_view_displays_book_that_are_available_and_on_loan(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertContains(response, 'Copies of Individual Books in the Library')
        self.assertNotContains(response, 'This copy is currently on Maintenance')
        self.assertNotContains(response, 'This copy is currently Reserved')
        for book in response.context['bookinstance_list']:
            if book.due_back is not None:
                self.assertContains(response, 'This copy is currently on loan')
            else:
                self.assertNotContains(response, 'This copy is currently Available')

    def test_view_display_book_that_are_on_maintenance_and_on_reserve(self):
        book = BookInstance.objects.all()
        status = {
            'maintenance': 'm',
            'reserved': 'r'
        }
        for book_copy in book:
            book_copy.due_back = None
            book_copy.status = \
                status['maintenance'] if book_copy.imprint == 'Abu Publishing House' else status['reserved']
            book_copy.save()

        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertContains(response, 'Copies of Individual Books in the Library')
        self.assertContains(response, 'This copy is currently on Maintenance')
        self.assertContains(response, 'This copy is currently Reserved')
        self.assertNotContains(response, 'This copy is currently Available')
        self.assertNotContains(response, 'This copy is currently on loan')

    def test_no_book_copy_in_library(self):
        BookInstance.objects.all().delete()
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertContains(response, 'There are no copies in the library.')


class LibrarianRenewBookViewTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='User', password='dhjhjhfj')
        self.test_librarian = User.objects.create(username='Librarian', password='12Thyr^')

        self.user_1.save()
        self.test_librarian.save()

        permission = Permission.objects.get(name='Renew date for books on loan')
        self.test_librarian.user_permissions.add(permission)
        self.test_librarian.save()

        test_author = Author.objects.create(first_name='John', last_name='Agbo')
        test_genre = Genre.objects.create(name='Igala comics')
        test_language = Language.objects.create(name='Idoma')
        test_book = Book.objects.create(
            title='Book Title',
            summary='Book Summary',
            isbn='7798uj',
            author=test_author,
            language=test_language

        )

        test_book.genre.set([test_genre, ])
        test_book.save()

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance_1 = BookInstance.objects.create(
            book=test_book,
            imprint='Printed June 11, 2020 1:01AM',
            due_back=return_date,
            borrower=self.user_1,
            status='o'
        )

        self.test_bookinstance_2 = BookInstance.objects.create(
            book=test_book,
            imprint='Printed June 11, 2020 1:03AM',
            due_back=return_date,
            borrower=self.test_librarian,
            status='o'
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('catalog:renew-book-librarian', kwargs={
            'pk': self.test_bookinstance_1.pk
        }))
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('catalog:renew-book-librarian', kwargs={
            'pk': self.test_bookinstance_1.pk}))

    def test_logged_in_with_with_permission_borrowed_book(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_2.pk}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Renew: {}'.format(self.test_bookinstance_1.book))

    def test_logged_in_with_permission_another_user_borrowed_book(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikekly UID to match our bookinstance
        test_uid = uuid.uuid4()
        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': test_uid}))
        self.assertEquals(response.status_code, 404)

    def test_correct_template_used(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertTemplateUsed(response, 'catalog/librarian_renew_book_copy.html')

    def test_form_renewal_date_initially_has_date_one_week_in_future(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        date_1_week_in_future = datetime.date.today() + datetime.timedelta(weeks=1)
        # Get method for the form has an initial due_back date of 1 week ahead
        self.assertEquals(response.context['form'].initial['due_back'], date_1_week_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        post_response = self.client.post(
            reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'due_back': valid_date_in_future})
        self.assertEquals(str(response.context['user']), 'Librarian')
        self.assertEquals(post_response.status_code, 200)
        self.assertTemplateUsed(post_response, 'catalog/librarian_all_book_copies_borrowed.html')

    def test_form_invalid_renewal_date_past(self):
        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        date_in_past = datetime.date.today() - datetime.timedelta(days=1)
        post_response = self.client.post(
            reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'due_back': date_in_past})
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'due_back', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        date_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        post_response = self.client.post(
            reverse('catalog:renew-book-librarian', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'due_back': date_in_future})
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'due_back', 'Invalid date - renewal more than 2 weeks ahead')


class UserBorrowBookViewTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='User', password='dhjhjhfj')
        self.user_1.save()

        self.user_2 = User.objects.create(username="Gtar", password='trhhkja')
        self.user_2.save()

        permission = Permission.objects.get(name='Users can make a borrow request')
        self.user_1.user_permissions.add(permission)
        self.user_1.save()

        test_author = Author.objects.create(first_name='John', last_name='Agbo')
        test_genre = Genre.objects.create(name='Igala comics')
        test_language = Language.objects.create(name='Idoma')
        test_book = Book.objects.create(
            title='Book Title',
            summary='Book Summary',
            isbn='7798uj',
            author=test_author,
            language=test_language

        )

        test_book.genre.set([test_genre, ])
        test_book.save()

        return_date = datetime.date.today() + datetime.timedelta(weeks=1)
        self.test_bookinstance_1 = BookInstance.objects.create(
            book=test_book,
            imprint='Printed June 11, 2020 1:01AM',
            due_back=return_date,
            borrower=self.user_1,
            status='a'
        )

        self.test_bookinstance_2 = BookInstance.objects.create(
            book=test_book,
            imprint='Printed June 11, 2020 1:01AM',
            due_back=return_date,
            borrower=self.user_2,
            status='a'
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('catalog:borrow_request', kwargs={
            'pk': self.test_bookinstance_1.pk
        }))
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.force_login(self.user_2)
        response = self.client.get(reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_2.pk}))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('catalog:borrow_request', kwargs={
            'pk': self.test_bookinstance_2.pk}))

    def test_logged_in_with_with_permission_borrowed_book(self):
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Borrow: {}'.format(self.test_bookinstance_1.book))
        self.assertContains(response,
                            'Note: Upon borrow request acceptance, book would be listed in your "My Borrowed Tab"'
                            )

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikekly UID to match our bookinstance
        test_uid = uuid.uuid4()
        self.client.force_login(user=self.user_1)
        response = self.client.get(reverse('catalog:borrow_request', kwargs={'pk': test_uid}))
        self.assertEquals(response.status_code, 404)

    def test_correct_template_used(self):
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertTemplateUsed(response, 'catalog/user_make_book_copy_borrow_request.html')

    def test_form_return_date_initially_has_date_two_week_in_future(self):
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        date_2_week_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        # Get method for the form has an initial due_back date of 2 week ahead
        self.assertEquals(response.context['form'].initial['due_back'], date_2_week_in_future)

    def test_redirects_to_all_user_books_copy_available_on_success(self):
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        post_response = self.client.post(
            reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'due_back': valid_date_in_future})
        self.assertEquals(str(response.context['user']), 'User')
        self.assertEquals(post_response.status_code, 200)
        self.assertTemplateUsed(post_response, 'catalog/user_book_copies_available.html')

    def test_form_invalid_return_date_past(self):
        self.client.force_login(user=self.user_1)
        response = self.client.get(reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        date_in_past = datetime.date.today() - datetime.timedelta(days=1)
        post_response = self.client.post(
            reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'due_back': date_in_past})
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'due_back', 'Invalid date - return date the in past')

    def test_form_invalid_return_date_future(self):
        self.client.force_login(user=self.user_1)
        response = self.client.get(reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        date_in_future = datetime.date.today() + datetime.timedelta(weeks=4)
        post_response = self.client.post(
            reverse('catalog:borrow_request', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'due_back': date_in_future})
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'due_back', 'Invalid date - return date more than 3 weeks ahead')


class LibrarianMarkCopyAsReturnedViewTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='User', password='dhjhjhfj')
        self.test_librarian = User.objects.create(username='Librarian', password='12Thyr^')

        self.user_1.save()
        self.test_librarian.save()

        permission = Permission.objects.get(name="Set book as returned")
        self.test_librarian.user_permissions.add(permission)
        self.test_librarian.save()

        test_author = Author.objects.create(first_name='John', last_name='Agbo')
        test_genre = Genre.objects.create(name='Igala comics')
        test_language = Language.objects.create(name='Idoma')
        test_book = Book.objects.create(
            title='Book Title',
            summary='Book Summary',
            isbn='7798uj',
            author=test_author,
            language=test_language

        )

        test_book.genre.set([test_genre, ])
        test_book.save()

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance_1 = BookInstance.objects.create(
            book=test_book,
            imprint='Printed June 11, 2020 1:01AM',
            due_back=return_date,
            borrower=self.user_1,
            status='o'
        )

        self.test_bookinstance_2 = BookInstance.objects.create(
            book=test_book,
            imprint='Printed June 11, 2020 1:03AM',
            due_back=return_date,
            borrower=self.test_librarian,
            status='o'
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('catalog:bookinstance_return', kwargs={
            'pk': self.test_bookinstance_1.pk
        }))
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_if_logged_in_but_not_correct_permission(self):
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 403)

    def test_logged_in_with_with_permission_mark_return(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_2.pk}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Edit this book to Mark as Return')

    def test_logged_in_with_permission_another_user_borrowed_book(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikekly UID to match our bookinstance
        test_uid = uuid.uuid4()
        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': test_uid}))
        self.assertEquals(response.status_code, 404)

    def test_correct_template_used(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertTemplateUsed(response, 'catalog/librarian_book_copy_mark_return.html')

    def test_redirects_to_all_borrowed_book_instance_list_on_success(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        form_data = {
            'borrower': '',
            'due_back': '',
            'status': 'a'
        }
        post_response = self.client.post(
            reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}),
            data=form_data)
        self.assertEquals(str(response.context['user']), 'Librarian')
        self.assertEquals(post_response.status_code, 302)
        self.assertRedirects(post_response, reverse('catalog:bookinstance_list'))

    def test_form_borrower_field_borrower_field_must_be_empty_error(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        form_data = {
            'borrower': self.user_1.pk,
            'due_back': '',
            'status': 'a'
        }
        post_response = self.client.post(
            reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}),
            data=form_data)
        self.assertEquals(str(response.context['user']), 'Librarian')
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'borrower', 'Borrower field must be empty" ')

    def test_form_status_field_you_must_mark_as_available_error(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        form_data = {
            'borrower': '',
            'due_back': '',
            'status': 'o'
        }
        post_response = self.client.post(
            reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}),
            data=form_data)
        self.assertEquals(str(response.context['user']), 'Librarian')
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'status', 'You must mark as "Available" ')

    def test_form_due_back_field_date_must_be_null_error(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        form_data = {
            'borrower': '',
            'due_back': '2020-02-28',
            'status': 'a'
        }
        post_response = self.client.post(
            reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}),
            data=form_data)
        self.assertEquals(str(response.context['user']), 'Librarian')
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'due_back', 'Date must be Null')

    def test_form_all_field_error(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        form_data = {
            'borrower': self.user_1.pk,
            'due_back': '2020-02-28',
            'status': 'o'
        }
        post_response = self.client.post(
            reverse('catalog:bookinstance_return', kwargs={'pk': self.test_bookinstance_1.pk}),
            data=form_data)
        self.assertEquals(str(response.context['user']), 'Librarian')
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'due_back', 'Date must be Null')
        self.assertFormError(post_response, 'form', 'status', 'You must mark as "Available" ')
        self.assertFormError(post_response, 'form', 'borrower', 'Borrower field must be empty" ')


class LibrarianApproveBorrowRequestViewTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='User', password='dhjhjhfj')
        self.test_librarian = User.objects.create(username='Librarian', password='12Thyr^')

        self.user_1.save()
        self.test_librarian.save()

        permission = Permission.objects.get(name='Renew date for books on loan')
        self.test_librarian.user_permissions.add(permission)
        self.test_librarian.save()

        test_author = Author.objects.create(first_name='John', last_name='Agbo')
        test_genre = Genre.objects.create(name='Igala comics')
        test_language = Language.objects.create(name='Idoma')
        test_book = Book.objects.create(
            title='Book Title',
            summary='Book Summary',
            isbn='7798uj',
            author=test_author,
            language=test_language

        )

        test_book.genre.set([test_genre, ])
        test_book.save()

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance_1 = BookInstance.objects.create(
            book=test_book,
            imprint='Printed June 11, 2020 1:01AM',
            due_back=return_date,
            borrower=self.user_1,
            status='o'
        )

        self.test_bookinstance_2 = BookInstance.objects.create(
            book=test_book,
            imprint='Printed June 11, 2020 1:03AM',
            due_back=return_date,
            borrower=self.test_librarian,
            status='o'
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('catalog:copy_approve', kwargs={
            'pk': self.test_bookinstance_1.pk
        }))
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('catalog:copy_approve', kwargs={
            'pk': self.test_bookinstance_1.pk}))

    def test_logged_in_with_with_permission_borrowed_book(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_2.pk}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Approve this book for borrow')

    def test_logged_in_with_permission_another_user_borrowed_book(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        # unlikekly UID to match our bookinstance
        test_uid = uuid.uuid4()
        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': test_uid}))
        self.assertEquals(response.status_code, 404)

    def test_correct_template_used(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertTemplateUsed(response, 'catalog/librarian_approve_borrow.html')

    def test_form_status_initial_is_available(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        initial_status = 'a'
        # Get method for the form has an initial due_back date of 1 week ahead
        self.assertEquals(response.context['form'].initial['status'], initial_status)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        self.client.force_login(self.test_librarian)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        post_response = self.client.post(
            reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'status': 'o'})
        self.assertEquals(str(response.context['user']), 'Librarian')
        self.assertEquals(post_response.status_code, 200)
        self.assertTemplateUsed(post_response, 'catalog/librarian_book_copy_borrow_approval_page.html')

    def test_form_invalid_status_available(self):
        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        post_response = self.client.post(
            reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'status': 'a'})
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'status', 'You must approve as "On-Loan" ')

    def test_form_invalid_status_reserved(self):
        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        post_response = self.client.post(
            reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'status': 'r'})
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'status', 'You must approve as "On-Loan" ')

    def test_form_invalid_status_maintenance(self):
        self.client.force_login(user=self.test_librarian)
        response = self.client.get(reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}))
        self.assertEquals(response.status_code, 200)
        post_response = self.client.post(
            reverse('catalog:copy_approve', kwargs={'pk': self.test_bookinstance_1.pk}),
            data={'status': 'm'})
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'status', 'You must approve as "On-Loan" ')


class CopyOfBookCreateViewTest(TestCase):

    def setUp(self):
        self.librarian_user = User.objects.create(username="librarian_user", password='123456')
        self.normal_user = User.objects.create(username='normal_user', password='7890')
        self.librarian_user.save()
        self.normal_user.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user.user_permissions.add(permission)
        self.librarian_user.save()

        self.test_book = Book.objects.create(title='A war Zone')

    def test_user_with_permission_can_view_create_bookinstance(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:bookinstance_create'))
        self.assertEquals(response.status_code, 200)

    # def test_user_with_permission_redirect_on_submit_of_bookinstance_create(self):
    #     self.client.force_login(user=self.librarian_user)
    #     response = self.client.get(reverse('catalog:bookinstance_create'))
    #     self.assertTemplateUsed(response, 'catalog/bookinstance_form.html')
    #     bookinstance_data = {
    #         'book': self.test_book,
    #         'imprint': 'Only God',
    #         'status': 'a'
    #     }
    #     self.assertContains(response, 'book')
    #     self.assertContains(response, 'imprint')
    #     self.assertContains(response, 'status')
    #     self.assertContains(response, 'Add copy of this book to the library records')
    #     post_response = self.client.post(reverse('catalog:bookinstance_create'), data=bookinstance_data)
    #     self.assertEquals(post_response.status_code, 302)
    # self.assertTemplateUsed(post_response, 'catalog/bookintsance_list.html')
    # self.assertRedirects(post_response, reverse('catalog:bookinstance_list')

    def test_user_without_permission_cant_access_view(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/catalog/bookcopy/create/')
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_bookinstance_create(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:bookinstance_create'))
        self.assertTemplateUsed(response, 'catalog/bookinstance_form.html')

    def test_invalid_status_entry_as_on_loan(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:bookinstance_create'))
        self.assertTemplateUsed(response, 'catalog/bookinstance_form.html')
        bookinstance_data = {
            'book': self.test_book,
            'imprint': 'Only God',
            'status': 'o'
        }
        self.assertContains(response, 'book')
        self.assertContains(response, 'imprint')
        self.assertContains(response, 'status')
        post_response = self.client.post(reverse('catalog:bookinstance_create'), data=bookinstance_data)
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'status', 'You must update as "Available" only!')

    def test_invalid_status_entry_as_reserved(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:bookinstance_create'))
        self.assertTemplateUsed(response, 'catalog/bookinstance_form.html')
        bookinstance_data = {
            'book': self.test_book,
            'imprint': 'Only God',
            'status': 'r'
        }
        self.assertContains(response, 'book')
        self.assertContains(response, 'imprint')
        self.assertContains(response, 'status')
        post_response = self.client.post(reverse('catalog:bookinstance_create'), data=bookinstance_data)
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'status', 'You must update as "Available" only!')

    def test_invalid_status_entry_as_maintenance(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:bookinstance_create'))
        self.assertTemplateUsed(response, 'catalog/bookinstance_form.html')
        bookinstance_data = {
            'book': self.test_book,
            'imprint': 'Only God',
            'status': 'm'
        }
        self.assertContains(response, 'book')
        self.assertContains(response, 'imprint')
        self.assertContains(response, 'status')
        post_response = self.client.post(reverse('catalog:bookinstance_create'), data=bookinstance_data)
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'status', 'You must update as "Available" only!')


class CopyOfBookUpdateViewTest(TestCase):
    def setUp(self):
        test_bookinstance = BookInstance.objects.create(imprint='Rachel publishing house', status='a')
        test_bookinstance.save()

        self.librarian_user1 = User.objects.create(username="librarian_user", password='12345')
        self.normal_user1 = User.objects.create(username='normal_user', password='78904')
        self.librarian_user1.save()
        self.normal_user1.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user1.user_permissions.add(permission)
        self.librarian_user1.save()

        self.bookinstance = BookInstance.objects.get(id=test_bookinstance.pk)

    def test_user_with_permission_can_update_all_field(self):
        self.client.force_login(user=self.librarian_user1)
        response = self.client.get(reverse('catalog:bookinstance_update', kwargs={'pk': self.bookinstance.id}))
        self.assertTemplateUsed(response, 'catalog/librarian_update_copy_of_book.html')

        # Check that the rendered view has original data from test_db
        self.assertEquals(self.bookinstance.imprint, 'Rachel publishing house')

        new_bookinstance_update = {'imprint': 'Joel publishing house',
                                   'status': 'r'
                                   }
        self.assertContains(response, 'imprint')
        self.assertContains(response, 'status')
        self.assertContains(response, 'Update this book')
        post_response = self.client.post(reverse('catalog:bookinstance_update', kwargs={'pk': self.bookinstance.id}),
                                         data=new_bookinstance_update)
        self.assertRedirects(post_response, reverse('catalog:bookinstance_list'))
        self.bookinstance.refresh_from_db()

        # Check that the original data has been updated to new data
        self.assertEquals(self.bookinstance.imprint, 'Joel publishing house')
        self.assertEquals(self.bookinstance.status, 'r')

    def test_user_with_permission_can_update_some_field(self):
        self.client.force_login(user=self.librarian_user1)
        response = self.client.get(reverse('catalog:bookinstance_update', kwargs={'pk': self.bookinstance.id}))
        self.assertTemplateUsed(response, 'catalog/librarian_update_copy_of_book.html')
        self.assertEquals(self.bookinstance.status, 'a')
        new_bookinstance_update = {
            'imprint': 'Rachel publishing house',
            'status': 'm',
        }
        self.assertContains(response, 'imprint')
        self.assertContains(response, 'status')
        self.assertContains(response, 'Update this book')
        post_response = self.client.post(reverse('catalog:bookinstance_update', kwargs={'pk': self.bookinstance.id}),
                                         data=new_bookinstance_update)
        self.assertRedirects(post_response, reverse('catalog:bookinstance_list'))
        self.bookinstance.refresh_from_db()

        # Check that the original status data has been updated to the new data
        self.assertEquals(self.bookinstance.status, 'm')

        # Check the imprint data still remained as at it were originally
        self.assertEquals(self.bookinstance.imprint, 'Rachel publishing house')

    def test_user_without_permission_cant_view_bookinstance_update(self):
        self.client.force_login(user=self.normal_user1)
        response = self.client.get(reverse('catalog:bookinstance_update', kwargs={'pk': self.bookinstance.id}))
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_bookinstance_update(self):
        self.client.force_login(user=self.librarian_user1)
        response = self.client.get(reverse('catalog:bookinstance_update', kwargs={'pk': self.bookinstance.id}))
        self.assertTemplateUsed(response, 'catalog/librarian_update_copy_of_book.html')

    def test_invalid_status_entry_as_on_loan(self):
        self.client.force_login(user=self.librarian_user1)
        response = self.client.get(reverse('catalog:bookinstance_update', kwargs={'pk': self.bookinstance.id}))
        self.assertTemplateUsed(response, 'catalog/librarian_update_copy_of_book.html')
        new_bookinstance_update = {
            'imprint': 'Rachel publishing house',
            'status': 'o',
        }
        self.assertContains(response, 'imprint')
        self.assertContains(response, 'status')
        self.assertContains(response, 'Update this book')
        post_response = self.client.post(reverse('catalog:bookinstance_update', kwargs={'pk': self.bookinstance.id}),
                                         data=new_bookinstance_update)
        self.assertEquals(post_response.status_code, 200)
        self.assertFormError(post_response, 'form', 'status',
                             'You must update as "Available" or "Maintenance" or "Reserved" only!')


class CopyOfBookDeleteViewTest(TestCase):
    def setUp(self):
        # Create 2 book copies for deletion test
        NUMBER_OF_BOOK_COPIES = 2

        test_book = Book.objects.create(title="Desires of a woman")
        for bookinstance_id in range(NUMBER_OF_BOOK_COPIES):
            test_bookinstance = BookInstance.objects.create(book=test_book,
                                                            imprint='Ella House {}'.format(bookinstance_id),
                                                            status='a'
                                                            )

        self.bookcopy = BookInstance.objects.get(id=test_bookinstance.pk)

        self.normal_user_1 = User.objects.create(username='normal', password='user')
        self.normal_user_1.save()

        self.librarian_user_1 = User.objects.create(username='librarian', password='useruser')
        self.librarian_user_1.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user_1.user_permissions.add(permission)
        self.librarian_user_1.save()

    def test_user_with_permission_can_view_book_copy_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:bookinstance_delete', kwargs={'pk': self.bookcopy.id}))
        self.assertEquals(response.status_code, 200)

    def test_user_without_permission_cant_view_book_copy_delete(self):
        self.client.force_login(user=self.normal_user_1)
        response = self.client.get(reverse('catalog:bookinstance_delete', kwargs={'pk': self.bookcopy.id}))
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_book_copy_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:bookinstance_delete', kwargs={'pk': self.bookcopy.id}))
        self.assertTemplateUsed(response, 'catalog/bookinstance_confirm_delete.html')

    def test_book_instance_deleted_successfully(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:bookinstance_delete', kwargs={'pk': self.bookcopy.id}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Are you sure you want to delete this book copy: {} ({})?'.format(
            self.bookcopy.id, self.bookcopy.book))
        self.assertEquals(self.bookcopy.book.title, 'Desires of a woman')
        self.assertEquals(self.bookcopy.imprint, 'Ella House 1')
        new_response = self.client.delete(reverse('catalog:bookinstance_delete', kwargs={'pk': self.bookcopy.id}))
        self.assertRedirects(new_response, reverse('catalog:bookinstance_list'))
        self.assertFalse(Author.objects.filter(id=self.bookcopy.id).exists())


class CopyOfBookListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 book copies for pagination tests
        NUMBER_OF_BOOK_COPIES = 13

        test_book = Book.objects.create(title='Oro house of poems')
        for book_copy_id in range(NUMBER_OF_BOOK_COPIES):
            BookInstance.objects.create(book=test_book, imprint='Chinwes Pub Homes',
                                        status='a' if book_copy_id % 2 else 'o'
                                        )

    def setUp(self):
        self.normal_user_1 = User.objects.create(username='normal', password='user')
        self.normal_user_1.save()

        self.librarian_user_1 = User.objects.create(username='librarian', password='useruser')
        self.librarian_user_1.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user_1.user_permissions.add(permission)
        self.librarian_user_1.save()

    def test_view_url_exists_at_desired_location(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get('/catalog/bookcopy/')
        self.assertEquals(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_templates(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_list.html')

    def test_pagination_is_nine(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "This copy is currently Available")
        self.assertContains(response, "This copy is currently on loan")
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['bookinstance_list']) == 6)

    def test_list_all_authors(self):
        self.client.force_login(user=self.librarian_user_1)
        # Get third page and confirm it has exactly remaining 1 item
        response = self.client.get(reverse('catalog:bookinstance_list') + '?page=3')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['bookinstance_list']) == 1)

    def test_unauthorized_user_denied_access_to_view(self):
        self.client.force_login(user=self.normal_user_1)
        response = self.client.get(reverse('catalog:bookinstance_list'))
        self.assertEquals(response.status_code, 403)


class BookCreateViewTest(TestCase):
    def setUp(self):
        self.librarian_user = User.objects.create(username="librarian_user", password='123456')
        self.normal_user = User.objects.create(username='normal_user', password='7890')
        self.librarian_user.save()
        self.normal_user.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user.user_permissions.add(permission)
        self.librarian_user.save()

        self.test_language = Language.objects.create(name='Ebira')
        self.test_author = Author.objects.create(first_name='Miracle', last_name='Onojason')
        self.test_genre_1 = Genre.objects.create(name='Fiction')
        self.test_genre_2 = Genre.objects.create(name='Documentary')

    def test_user_with_permission_can_view_create_book(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:book_create'))
        self.assertEquals(response.status_code, 200)

    # def test_user_with_permission_redirect_on_submit_of_book_create(self):
    #     self.client.force_login(user=self.librarian_user)
    #     response = self.client.get(reverse('catalog:book_create'))
    #     self.assertTemplateUsed(response, 'catalog/book_form.html')
    #     book_data = {'title': 'A Liars Den',
    #                  'author': self.test_author,
    #                  'summary': 'Its a wild wild west out there',
    #                  'isbn': '1678989752b',
    #                  'genre': [self.test_genre_1, self.test_genre_2],
    #                  'language': self.test_language
    #                  }
    #     self.assertContains(response, 'Title')
    #     self.assertContains(response, 'Author')
    #     self.assertContains(response, 'Summary')
    #     self.assertContains(response, 'ISBN')
    #     self.assertContains(response, 'Genre')
    #     self.assertContains(response, 'Language')
    #     post_response = self.client.post(reverse('catalog:book_create'), data=book_data)
    #     # self.assertEquals(post_response.status_code, 302)
    #     self.assertRedirects(post_response, reverse('catalog:book-detail', kwargs={'pk': 1}))

    def test_user_without_permission_cant_access_view(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/catalog/books/create/')
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_book_create(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:book_create'))
        self.assertTemplateUsed(response, 'catalog/book_form.html')


class BookUpdateViewTest(TestCase):
    def setUp(self):
        test_language = Language.objects.create(name='Bassa')
        test_author = Author.objects.create(first_name='Ella', last_name='Immanuel')
        test_genre_1 = Genre.objects.create(name='History')
        test_genre_2 = Genre.objects.create(name='Horror')
        genre_list = [test_genre_1, test_genre_2]
        test_book = Book.objects.create(title='OYO for you', author=test_author, language=test_language,
                                        isbn='576yhjhjd', summary='I don\'t know what to type')

        test_book.genre.set(genre_list)
        test_book.save()

        self.librarian_user1 = User.objects.create(username="librarian_user", password='12345')
        self.normal_user1 = User.objects.create(username='normal_user', password='78904')
        self.librarian_user1.save()
        self.normal_user1.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user1.user_permissions.add(permission)
        self.librarian_user1.save()

        self.book = Book.objects.get(id=test_book.pk)

    # def test_user_with_permission_can_update_all_field(self):
    #     test_language_update = Language.objects.create(name='Igala')
    #     test_author_update = Author.objects.create(first_name='Arome', last_name='Achimugu')
    #     test_genre_update = Genre.objects.create(name='Romance')
    #     self.client.force_login(user=self.librarian_user1)
    #     response = self.client.get(reverse('catalog:book_update', kwargs={'pk': self.book.id}))
    #     self.assertTemplateUsed(response, 'catalog/book_form.html')
    #
    #     # Check that the rendered view has original data from test_db
    #     self.assertEquals(self.book.title, 'OYO for you')
    #     self.assertEquals(str(self.book.author), 'Immanuel, Ella')
    #
    #     new_book_update = {'title': 'Dunno my name',
    #                        'author': test_author_update,
    #                        'language': test_language_update,
    #                        'summary': 'I really wanna get married',
    #                        'isbn': '5379888uhnd',
    #                        'genre': test_genre_update
    #                        }
    #     self.assertContains(response, 'Title')
    #     self.assertContains(response, 'Summary')
    #     self.assertContains(response, 'Genre')
    #     post_response = self.client.post(reverse('catalog:book_update', kwargs={'pk': self.book.id}),
    #                                      data=new_book_update)
    #     self.assertRedirects(post_response, reverse('catalog:book-detail', kwargs={'pk': self.book.id}))
    #     self.book.refresh_from_db()
    #
    #     # Check that the original data has been updated to new data
    #     self.assertEquals(self.book.author.first_name, 'Arome')
    #     self.assertEquals(self.book.genre, 'Romance')
    #     self.assertEquals(self.book.title, 'Dunno my name')
    #
    # def test_user_with_permission_can_update_some_field(self):
    #     test_language_update = Language.objects.create(name='Igbo')
    #     test_author_update = Author.objects.create(first_name='Ella', last_name='Achimugu')
    #     test_genre_update = Genre.objects.create(name='Thriller')
    #     self.client.force_login(user=self.librarian_user1)
    #     response = self.client.get(reverse('catalog:book_update', kwargs={'pk': self.book.id}))
    #     self.assertTemplateUsed(response, 'catalog/book_form.html')
    #     self.assertEquals(self.book.author.last_name, 'Immanuel')
    #     new_book_update = {'title': 'OYO for you',
    #                        'author': test_author_update,
    #                        'language': test_language_update,
    #                        'summary': 'I don\'t know what to type',
    #                        'isbn': '576yhjhjd',
    #                        'genre': test_genre_update
    #                        }
    #     self.assertContains(response, 'ISBN')
    #     self.assertContains(response, 'Author')
    #     self.assertContains(response, 'Language')
    #     post_response = self.client.post(reverse('catalog:book_update', kwargs={'pk': self.book.id}),
    #                                      data=new_book_update)
    #     self.assertRedirects(post_response, reverse('catalog:book-detail', kwargs={'pk': self.book.id}))
    #     self.book.refresh_from_db()
    #
    #     # Check that the original last_name data has been updated to the new data
    #     self.assertEquals(self.book.author.last_name, 'Achimugu')
    #
    #     # Check the author first_name data still remained at it were originally
    #     self.assertEquals(self.book.author.first_name, 'Ella')

    def test_user_without_permission_cant_view_book_update(self):
        self.client.force_login(user=self.normal_user1)
        response = self.client.get(reverse('catalog:book_update', kwargs={'pk': self.book.id}))
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_author_update(self):
        self.client.force_login(user=self.librarian_user1)
        response = self.client.get(reverse('catalog:book_update', kwargs={'pk': self.book.id}))
        self.assertTemplateUsed(response, 'catalog/book_form.html')
        self.assertEquals(response.status_code, 200)


class BookDetailViewTest(TestCase):
    def setUp(self):
        test_language = Language.objects.create(name='Bassa')
        test_author = Author.objects.create(first_name='Ella', last_name='Immanuel')
        test_genre_1 = Genre.objects.create(name='History')
        test_genre_2 = Genre.objects.create(name='Horror')
        genre_list = [test_genre_1, test_genre_2]
        test_book = Book.objects.create(title='OYO for you', author=test_author, language=test_language,
                                        isbn='576yhjhjd', summary='I don\'t know what to type')

        test_book.genre.set(genre_list)
        test_book.save()

        self.book = Book.objects.get(id=test_book.pk)

    def test_book_detail_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse('catalog:book-detail', kwargs={'pk': self.book.id}))
        self.assertEquals(response.status_code, 200)

    def test_book_detail_does_not_exist(self):
        response = self.client.get('/catalog/books/2/')
        self.assertEquals(response.status_code, 404)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('catalog:book-detail', kwargs={'pk': self.book.id}))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('catalog:book-detail', kwargs={'pk': self.book.id}))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_detail.html')


class BookDeleteViewTest(TestCase):
    def setUp(self):
        # Create 2 books for deletion test

        test_language = Language.objects.create(name='Bassa')
        test_author = Author.objects.create(first_name='Ella', last_name='Immanuel')

        NUMBER_OF_BOOKS = 2

        for book_id in range(NUMBER_OF_BOOKS):
            test_book = Book.objects.create(title='OYO for you {}'.format(book_id), author=test_author,
                                            language=test_language, isbn='576yhjhjd',
                                            summary='I don\'t know what to type')

        self.book = Book.objects.get(id=test_book.pk)

        self.normal_user_1 = User.objects.create(username='normal', password='user')
        self.normal_user_1.save()

        self.librarian_user_1 = User.objects.create(username='librarian', password='useruser')
        self.librarian_user_1.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user_1.user_permissions.add(permission)
        self.librarian_user_1.save()

    def test_user_with_permission_can_view_book_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:book_delete', kwargs={'pk': self.book.id}))
        self.assertEquals(response.status_code, 200)

    def test_user_without_permission_cant_view_book_delete(self):
        self.client.force_login(user=self.normal_user_1)
        response = self.client.get(reverse('catalog:book_delete', kwargs={'pk': self.book.id}))
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_book_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:book_delete', kwargs={'pk': self.book.id}))
        self.assertTemplateUsed(response, 'catalog/book_confirm_delete.html')

    def test_author_deleted_successfully(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:book_delete', kwargs={'pk': self.book.id}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Are you sure you want to delete the book: {}?'.format(self.book.title))
        self.assertEquals(self.book.title, 'OYO for you 1')
        self.assertEquals(self.book.genre.name, None)
        new_response = self.client.delete(reverse('catalog:book_delete', kwargs={'pk': self.book.id}))
        self.assertRedirects(new_response, reverse('catalog:book-list'))
        self.assertFalse(Author.objects.filter(id=self.book.id).exists())


class BookListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_language = Language.objects.create(name='Bassa')
        test_author = Author.objects.create(first_name='Ella', last_name='Immanuel')

        NUMBER_OF_BOOKS = 13

        for book_id in range(NUMBER_OF_BOOKS):
            Book.objects.create(title='OYO for you {}'.format(book_id), author=test_author,
                                language=test_language, isbn='576yhjhjd',
                                summary='I don\'t know what to type')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/books/')
        self.assertEquals(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('catalog:book-list'))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_templates(self):
        response = self.client.get(reverse('catalog:book-list'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book.html')

    def test_pagination_is_nine(self):
        response = self.client.get(reverse('catalog:book-list'))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['list_of_books']) == 9)

    def test_list_all_books(self):
        # Get second page and confirm it has exactly remaining 4 items
        response = self.client.get(reverse('catalog:book-list') + '?page=2')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['list_of_books']) == 4)


class GenreCreateViewTest(TestCase):
    def setUp(self):
        self.librarian_user = User.objects.create(username="librarian_user", password='123456')
        self.normal_user = User.objects.create(username='normal_user', password='7890')
        self.librarian_user.save()
        self.normal_user.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user.user_permissions.add(permission)
        self.librarian_user.save()

    def test_user_with_permission_can_view_create_genre(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:genre_create'))
        self.assertEquals(response.status_code, 200)

    def test_user_with_permission_redirect_on_submit_of_genre_create(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:genre_create'))
        self.assertTemplateUsed(response, 'catalog/genre_form.html')
        genre_data = {'name': 'Romance'}
        self.assertContains(response, 'name')
        new_response = self.client.post(reverse('catalog:genre_create'), data=genre_data)
        self.assertEquals(new_response.status_code, 302)
        # self.assertRedirects(new_response, reverse('catalog:author-detail', kwargs={'pk': 1}))

    def test_user_without_permission_cant_access_view(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/catalog/genres/create/')
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_genre_create(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:genre_create'))
        self.assertTemplateUsed(response, 'catalog/genre_form.html')


class GenreListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 Genres for pagination tests
        NUMBER_OF_AUTHORS = 13

        for genre_id in range(NUMBER_OF_AUTHORS):
            Genre.objects.create(name='Documentary {}'.format(genre_id))

    def setUp(self):
        self.librarian_user = User.objects.create(username="librarian_user", password='123456')
        self.normal_user = User.objects.create(username='normal_user', password='7890')
        self.librarian_user.save()
        self.normal_user.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user.user_permissions.add(permission)
        self.librarian_user.save()

    def test_not_logged_user_redirects(self):
        response = self.client.get('/catalog/genres/')
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('catalog:genre_list'))
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_unauthorized_user_denied_permission(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get(reverse('catalog:genre_list'))
        self.assertEquals(response.status_code, 403)

    def test_view_url_exists_at_desired_location(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get('/catalog/genres/')
        self.assertEquals(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:genre_list'))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_templates(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:genre_list'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/genre_list.html')

    def test_pagination_is_nine(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:genre_list'))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['genre_list']) == 9)

    def test_list_all_genres(self):
        # Get second page and confirm it has exactly remaining 4 items
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:genre_list') + '?page=2')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['genre_list']) == 4)


class LanguageDeleteViewTest(TestCase):
    def setUp(self):
        # Create 2 Genres for deletion test
        NUMBER_OF_LANGUAGES = 2

        for genre_id in range(NUMBER_OF_LANGUAGES):
            test_genre = Genre.objects.create(name='Romance {}'.format(genre_id))

        self.genre = Genre.objects.get(id=test_genre.pk)

        self.normal_user_1 = User.objects.create(username='normal', password='user')
        self.normal_user_1.save()

        self.librarian_user_1 = User.objects.create(username='librarian', password='useruser')
        self.librarian_user_1.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user_1.user_permissions.add(permission)
        self.librarian_user_1.save()

    def test_user_with_permission_can_view_genre_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:genre_delete', kwargs={'pk': self.genre.id}))
        self.assertEquals(response.status_code, 200)

    def test_user_without_permission_cant_view_genre_delete(self):
        self.client.force_login(user=self.normal_user_1)
        response = self.client.get(reverse('catalog:genre_delete', kwargs={'pk': self.genre.id}))
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_genre_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:genre_delete', kwargs={'pk': self.genre.id}))
        self.assertTemplateUsed(response, 'catalog/genre_confirm_delete.html')

    def test_language_deleted_successfully(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:genre_delete', kwargs={'pk': self.genre.id}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Are you sure you want to delete the genre: {}?'.format(self.genre))
        self.assertEquals(self.genre.name, 'Romance 1')
        new_response = self.client.delete(reverse('catalog:genre_delete', kwargs={'pk': self.genre.id}))
        self.assertRedirects(new_response, reverse('catalog:genre_list'))
        self.assertFalse(Genre.objects.filter(id=self.genre.id).exists())


class LanguageCreateViewTest(TestCase):
    def setUp(self):
        self.librarian_user = User.objects.create(username="librarian_user", password='123456')
        self.normal_user = User.objects.create(username='normal_user', password='7890')
        self.librarian_user.save()
        self.normal_user.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user.user_permissions.add(permission)
        self.librarian_user.save()

    def test_user_with_permission_can_view_create_language(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:language_create'))
        self.assertEquals(response.status_code, 200)

    def test_user_with_permission_redirect_on_submit_of_language_create(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:language_create'))
        self.assertTemplateUsed(response, 'catalog/language_form.html')
        language_data = {'name': 'Igala'}
        self.assertContains(response, 'name')
        new_response = self.client.post(reverse('catalog:language_create'), data=language_data)
        self.assertEquals(new_response.status_code, 302)
        # self.assertRedirects(new_response, reverse('catalog:author-detail', kwargs={'pk': 1}))

    def test_user_without_permission_cant_access_view(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get('/catalog/languages/create/')
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_genre_create(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:language_create'))
        self.assertTemplateUsed(response, 'catalog/language_form.html')


class LanguageListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 languages for pagination tests
        NUMBER_OF_AUTHORS = 13

        for language_id in range(NUMBER_OF_AUTHORS):
            Language.objects.create(name='Igala {}'.format(language_id))

    def setUp(self):
        self.librarian_user = User.objects.create(username="librarian_user", password='123456')
        self.normal_user = User.objects.create(username='normal_user', password='7890')
        self.librarian_user.save()
        self.normal_user.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user.user_permissions.add(permission)
        self.librarian_user.save()

    def test_not_logged_user_redirects(self):
        response = self.client.get('/catalog/genres/')
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + reverse('catalog:genre_list'))
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_unauthorized_user_denied_permission(self):
        self.client.force_login(user=self.normal_user)
        response = self.client.get(reverse('catalog:language_list'))
        self.assertEquals(response.status_code, 403)

    def test_view_url_exists_at_desired_location(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get('/catalog/languages/')
        self.assertEquals(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:language_list'))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_templates(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:language_list'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/language_list.html')

    def test_pagination_is_nine(self):
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:language_list'))
        self.assertEquals(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['language_list']) == 9)

    def test_list_all_languages(self):
        # Get second page and confirm it has exactly remaining 4 items
        self.client.force_login(user=self.librarian_user)
        response = self.client.get(reverse('catalog:language_list') + '?page=2')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertTrue(len(response.context['language_list']) == 4)


class LanguageDeleteViewTest(TestCase):
    def setUp(self):
        # Create 2 languages for deletion test
        NUMBER_OF_LANGUAGES = 2

        for language_id in range(NUMBER_OF_LANGUAGES):
            test_language = Language.objects.create(name='Ibibio {}'.format(language_id))

        self.language = Language.objects.get(id=test_language.pk)

        self.normal_user_1 = User.objects.create(username='normal', password='user')
        self.normal_user_1.save()

        self.librarian_user_1 = User.objects.create(username='librarian', password='useruser')
        self.librarian_user_1.save()

        permission = Permission.objects.get(name='Set book as returned')
        self.librarian_user_1.user_permissions.add(permission)
        self.librarian_user_1.save()

    def test_user_with_permission_can_view_language_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:language_delete', kwargs={'pk': self.language.id}))
        self.assertEquals(response.status_code, 200)

    def test_user_without_permission_cant_view_language_delete(self):
        self.client.force_login(user=self.normal_user_1)
        response = self.client.get(reverse('catalog:language_delete', kwargs={'pk': self.language.id}))
        self.assertEquals(response.status_code, 403)

    def test_correct_template_used_for_language_delete(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:language_delete', kwargs={'pk': self.language.id}))
        self.assertTemplateUsed(response, 'catalog/language_confirm_delete.html')

    def test_language_deleted_successfully(self):
        self.client.force_login(user=self.librarian_user_1)
        response = self.client.get(reverse('catalog:language_delete', kwargs={'pk': self.language.id}))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Are you sure you want to delete the language: {}?'.format(self.language))
        self.assertEquals(self.language.name, 'Ibibio 1')
        new_response = self.client.delete(reverse('catalog:language_delete', kwargs={'pk': self.language.id}))
        self.assertRedirects(new_response, reverse('catalog:language_list'))
        self.assertFalse(Language.objects.filter(id=self.language.id).exists())


class IndexViewTest(TestCase):
    def test_index_page_returns_normally(self):
        response = self.client.get(reverse('catalog:index'))
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, '127.0.0.1:8000/catalog/')


