"""
NOTE: For models with foreign key or any other dependency from other models, use setUp(self) class only and get
the id dynamically, but for stand alone models with no dependency on other model, you can use setUpTestData(cls).
"""

import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.models import Author, Genre, Book, BookInstance, Language, User


# Create your tests here
class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Run only once to set up non-modified data for all class methods defined below"""
        author = Author.objects.create(first_name='Rachel', last_name='Onojason')
        author.save()

    def setUp(self):
        """Run before every test method below is executed, to setup clean data"""
        # Get an author object to test
        self.author = Author.objects.get(id=1)

    def test_first_name_label(self):
        """Returns True if first_name == first name"""

        # Get the metadata for the required field and use it to query the required field data
        field_label = self.author._meta.get_field('first_name').verbose_name

        # Compare the value to the expected result
        self.assertEquals(field_label, 'first name')

    def test_first_name_max_length(self):
        """Returns True if the max_length for this field == 100"""
        max_length = self.author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_author_has_first_name(self):
        expected_first_name = self.author.first_name
        self.assertEquals(expected_first_name, "Rachel")

    def test_last_name_label(self):
        """Returns True if last_name == last name"""
        field_label = self.author._meta.get_field('last_name').verbose_name
        self.assertEquals(field_label, 'last name')

    def test_last_name_max_length(self):
        """Returns True if max_length for this field == 100"""
        max_length = self.author._meta.get_field('last_name').max_length
        self.assertEquals(max_length, 100)

    def test_author_has_last_name(self):
        expected_last_name = self.author.last_name
        self.assertEquals(expected_last_name, "Onojason")

    def test_date_of_death_label(self):
        """Returns True if date_ofDeath == died"""
        field_label = self.author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(field_label, 'died')

    def test_date_of_death_is_null(self):
        expected_death_date = self.author.date_of_death
        self.assertEquals(expected_death_date, None)

    def test_date_of_birth_label(self):
        """returns True if date_of_birth == date of birth"""
        field_label = self.author._meta.get_field('date_of_birth').verbose_name
        self.assertEquals(field_label, 'date of birth')

    def test_date_of_birth_default_(self):
        help_text_value = self.author._meta.get_field('date_of_birth').help_text
        self.assertEquals(help_text_value, 'yyyy-mm-dd')


    def test_date_of_birth_is_null(self):
        expected_birth_date = self.author.date_of_birth
        self.assertEquals(expected_birth_date, None)

    def test_author_object_is_last_name_comma_first_name(self):
        """Returns True if last_name, first_name == Onojason, Rachel"""
        expected_object_name = "{}, {}".format(self.author.last_name, self.author.first_name)
        self.assertEquals(expected_object_name, str(self.author))

    def test_get_absolute_url(self):
        """Returns True if the url config for author detail is present in app urls.py
        as specified there == /catalog/authors/<int:pk>/"""

        # Ensure the urlconf is defined before running this test, if not, it will fail
        # catalog is here because there is a redirect from home to 127.0.0.1:8000/catalog/ in base urls.py
        expected_url = '/catalog/authors/1/'
        self.assertEquals(expected_url, self.author.get_absolute_url())


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        genre = Genre.objects.create(name='Thriller')
        genre.save()

    def setUp(self):
        # using name attribute here instead of id, because this model has only one field(name)
        self.genre = Genre.objects.get(name='Thriller')

    def test_name_label(self):
        field_label = self.genre._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_name_max_length(self):
        max_length = self.genre._meta.get_field('name').max_length
        self.assertEquals(max_length, 200)

    def test_name_help_text(self):
        help_text = self.genre._meta.get_field('name').help_text
        self.assertEquals(help_text,
                          "Enter a book genre (e.g. Science Fiction)"
                          )

    def test_genre_has_name(self):
        expected_name = self.genre.name
        self.assertEquals(expected_name, 'Thriller')

    def test_genre_object_is_genre_name(self):
        expected_object_name = "{}".format(self.genre.name)
        self.assertEquals(expected_object_name, str(self.genre))

    def test_get_absolute_url(self):
        expected_url = '/catalog/genres/'
        self.assertEquals(expected_url, self.genre.get_absolute_url())


class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        language = Language.objects.create(name='Igala')
        language.save()

    def setUp(self):
        # using name attribute here instead of id, because this model has only one field(name)
        self.language = Language.objects.get(name='Igala')

    def test_name_label(self):
        field_label = self.language._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_name_max_length(self):
        max_length = self.language._meta.get_field('name').max_length
        self.assertEquals(max_length, 100)

    def test_name_help_text(self):
        help_text = self.language._meta.get_field('name').help_text
        self.assertEquals(help_text,
                          "Enter the book's natural language (e.g. English, French, Japanese etc.)"
                          )

    def test_language_has_name(self):
        expected_name = self.language.name
        self.assertEquals(expected_name, 'Igala')

    def test_get_absolute_url(self):
        expected_url = '/catalog/languages/'
        self.assertEquals(expected_url, self.language.get_absolute_url())

    def test_language_object_is_language_name(self):
        expected_object_name = "{}".format(self.language.name)
        self.assertEquals(expected_object_name, str(self.language))


class BookModelTest(TestCase):
    def setUp(self):
        """
            This model has a foreign key relationship and a many to many relationship with
            Model Genre, so the SetUpTestData function would be different from other test models
        """
        # Creating the foreign key instances
        author = Author.objects.create(first_name='Rachel Ene', last_name='Abu')
        language = Language.objects.create(name='Idoma')

        book_object = Book.objects.create(title='A Girl Meets Boy',
                                          summary='About a girls journey to love', isbn='1234567890123',
                                          author=author, language=language
                                          )
        # Creating many genre instances for one book
        self.genre_1 = Genre.objects.create(name='Romance')
        self.genre_2 = Genre.objects.create(name='Fiction')

        # Adding the genre objects to the book instance
        book_object.genre.set([self.genre_1.pk, self.genre_2.pk])
        book_object.save()

        self.book = Book.objects.get(id=book_object.pk)

    def test_one_book_has_many_genres(self):
        genre_count = self.book.genre.count()
        self.assertEquals(genre_count, 2)

    def test_book_has_author(self):
        expected_author = "{}, {}".format(self.book.author.last_name, self.book.author.first_name)
        self.assertEquals(expected_author, "Abu, Rachel Ene")

    def test_book_has_language(self):
        expected_language = self.book.language.name
        self.assertEquals(expected_language, "Idoma")

    def test_title_label(self):
        field_label = self.book._meta.get_field('title').verbose_name
        self.assertEquals(field_label, 'title')

    def test_title_max_length(self):
        max_length = self.book._meta.get_field('title').max_length
        self.assertEquals(max_length, 200)

    def test_book_has_title(self):
        expected_title = self.book.title
        self.assertEquals(expected_title, "A Girl Meets Boy"
                          )

    def test_author_label(self):
        field_label = self.book._meta.get_field('author').verbose_name
        self.assertEquals(field_label, 'author')

    def test_summary_label(self):
        field_label = self.book._meta.get_field('summary').verbose_name
        self.assertEquals(field_label, 'summary')

    def test_summary_max_length(self):
        max_length = self.book._meta.get_field('summary').max_length
        self.assertEquals(max_length, 1000)

    def test_summary_help_text(self):
        help_text = self.book._meta.get_field('summary').help_text
        self.assertEquals(help_text,
                          'Enter a brief description of the book')

    def test_book_has_summary(self):
        expected_summary = self.book.summary
        self.assertEquals(expected_summary,
                          "About a girls journey to love",
                          )

    def test_isbn_label(self):
        field_label = self.book._meta.get_field('isbn').verbose_name
        self.assertEquals(field_label, 'ISBN')

    def test_isbn_max_length(self):
        max_length = self.book._meta.get_field('isbn').max_length
        self.assertEquals(max_length, 13)

    def test_isbn_help_text(self):
        help_text = self.book._meta.get_field('isbn').help_text
        self.assertEquals(help_text,
                          '13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>'
                          )

    def test_book_has_isbn(self):
        expected_isbn = self.book.isbn
        self.assertEquals(expected_isbn, "1234567890123")

    def test_genre_label_name(self):
        field_label = self.book._meta.get_field('genre').verbose_name
        self.assertEquals(field_label, 'genre')

    def test_genre_help_text(self):
        help_text = self.book._meta.get_field('genre').help_text
        self.assertEquals(help_text,
                          "Select a genre for this book or press shift key and select more"
                          " to select more than one Genre"
                          )

    def test_language_label(self):
        field_label = self.book._meta.get_field('language').verbose_name
        self.assertEquals(field_label, 'language')

    def test_display_genre(self):
        display_genre = "{0}, {1}".format(self.book.genre.get(id=self.genre_1.pk),
                                          self.book.genre.get(id=self.genre_2.pk)
                                          )
        self.assertEquals(display_genre, self.book.display_genre())

    def test_book_object_is_book_title(self):
        expected_object_name = '{}'.format(self.book.title)
        self.assertEquals(expected_object_name, str(self.book))

    def test_get_absolute_url(self):
        expected_url = reverse('catalog:book-detail', kwargs={'pk': self.book.id})
        self.assertEquals(expected_url, self.book.get_absolute_url())


class BookInstanceModelTest(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='User', password='dhjhjhfj')
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

        return_date = datetime.date.today() + datetime.timedelta(days=5)
        test_bookinstance_1 = BookInstance.objects.create(
            book=test_book,
            imprint='Printed June 11, 2020 1:01AM',
            due_back=return_date,
            borrower=self.user_1,
            status='o'
        )

        self.book_instance = BookInstance.objects.get(id=test_bookinstance_1.pk)

    def test_book_label_name(self):
        field_label = self.book_instance._meta.get_field('book').verbose_name
        self.assertEquals(field_label, 'book')

    def test_imprint_label_name(self):
        field_label = self.book_instance._meta.get_field('imprint').verbose_name
        self.assertEquals(field_label, 'imprint')

    def test_due_back_label_name(self):
        field_label = self.book_instance._meta.get_field('due_back').verbose_name
        self.assertEquals(field_label, 'due back')

    def test_borrower_label_name(self):
        field_label = self.book_instance._meta.get_field('borrower').verbose_name
        self.assertEquals(field_label, 'borrower')

    def test_status_label_name(self):
        field_label = self.book_instance._meta.get_field('status').verbose_name
        self.assertEquals(field_label, 'status')

    def test_bookinstance_object_is_bookinstance_id_and_bookinstance_book_title(self):
        expected_object_name = '{0} ({1})'.format(self.book_instance.id, self.book_instance.book.title)
        self.assertEquals(expected_object_name, str(self.book_instance))

    def test_bookinstance_get_absolute_url(self):
        expected_url = '/catalog/bookcopy/'
        self.assertEquals(expected_url, self.book_instance.get_absolute_url())

    def test_book_instance_has_permissions(self):
        self.assertTrue(self.book_instance._meta.permissions)

    def test_bookinstance_is_overdue_true(self):
        new_due_back = datetime.date.today() - datetime.timedelta(weeks=2)
        self.book_instance.due_back = new_due_back
        self.assertTrue(self.book_instance.is_overdue)

    def test_bookinstance_is_overdue_false(self):
        new_due_back = datetime.date.today() + datetime.timedelta(weeks=2)
        self.book_instance.due_back = new_due_back
        self.assertFalse(self.book_instance.is_overdue)

    def test_bookinstance_status_field_displays_choices(self):
        field_label = self.book_instance._meta.get_field('status').choices
        self.assertEquals(field_label, (('m', 'Maintenance'), ('o', 'On Loan'), ('a', 'Available'), ('r', 'Reserved')))

    def test_bookinstance_status_default_choice(self):
        default_choice = self.book_instance._meta.get_field('status').default
        self.assertEquals(default_choice, 'a')
