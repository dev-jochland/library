import datetime

from django.db import models
from django.db.models import Q
from django.urls import reverse  # Used to generate URLs by reversing the URL patterns
import uuid  # Required for unique book instances
from datetime import date
from django.contrib.auth.models import User, Group
from django.utils import timezone


class Genre(models.Model):
    """Model representing a book genre"""
    name = models.CharField(
        max_length=200,
        help_text='Enter a book genre (e.g. Science Fiction)')

    # ordering is needed to avoid the "UnorderedObjectListWarning: Pagination may yield inconsistent results with
    # an unordered object_list" error on Pagination in a ListView.
    class Meta:
        ordering = ['name', ]

    # This is here to ensure a CreateView in views.py and on the html page has
    # a redirect url on Create Submit Button click
    def get_absolute_url(self):
        """Returns the url to access list of Genres added."""
        return reverse('catalog:genre_list')

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)")

    class Meta:
        ordering = ['name', ]

    # This is here to ensure a CreateView in views.py and on the html page has
    # a redirect url on Create Submit Button click
    def get_absolute_url(self):
        """Returns the url to access list of added Languages."""
        return reverse('catalog:language_list')

    def __str__(self):
        return self.name


class BookManager(models.Manager):
    """This model handles every search query for the Book Model"""
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(title__icontains=query) |
                         Q(author__icontains=query)
                         )
            qs = qs.filter(or_lookup).distinct()
        return qs


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<tourist_centre_name>/<filename>
    return '{0}/{1}'.format(instance.author.__str__(), filename)


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)

    # Foreign key used here because book can only have one author, but authors can have multiple
    # books(OneToMany ==> ForeignKey in Django

    # on_delete = models.SET_NULL, which will set the value of the author to
    # Null if the associated author record is deleted.

    # 'Author' is in quotes here since the class is referenced here
    # before the creation, as python is a sequential language
    author = models.ForeignKey('Author', on_delete=models.CASCADE, null=True)
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    book_cover = models.ImageField(upload_to=user_directory_path)
    # ManyToManyField used because genre can contain many books. Books can cover many genres
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book or press shift key '
                                                    'and select more to select more than one Genre')

    # A book can be written in one language, a Language can be used to write 0 or many books
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True)

    objects = BookManager()

    def display_genre(self):
        """Creates a string for the Genre. This is required to display genre in Admin.
        Because Genre is a Many to Many Field"""
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    # This is here to ensure a CreateView/UpdateView in views.py and on the html page has
    # a redirect url on Create/Update Submit Button click
    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""

        # if there were no app_name set in app/urls.py, it would have been just 'book-detail'
        return reverse('catalog:book-detail', args=[str(self.id)])


# In a typical OneToManyRelationship (Foreign Key) like below, BookInstance is not declared as a field in Book,
# so therefore BookInstance doesn't have any field to get the set of associated records.
# To overcome this problem, Django constructs an appropriately named "reverse lookup" function that you can use.
# The name of the function is constructed by lower-casing the model name where the ForeignKey was declared,
# followed by _set (i.e. so the function created in Book is bookinstance_set()).

# In the 'book_detail.html', book.bookinstance_set.all() was called to create an association as explained above.
# Note: Here I use all() to get all records (the default), also beware that if you don't define an order
# (on your class-based view or model), you will also see errors from the development server. That happens because
# the paginator object expects to see some ORDER BY being executed on the underlying database.

# Note: Always try to sort by an attribute/column that actually has an index (unique or not) on the database to
# avoid performance issues.


class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    # UUIDField is used for the id field to set it as the primary_key for this model. This type of
    # field allocates a globally unique value for each instance (one for every book you can find in the library)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text='Unique ID for this particular book across whole library')

    # each book can have many copies, but a copy can only have one Book
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On Loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='a',
        help_text='Book Availability')

    # The column below makes it possible for users to have a BookInstance
    # on loan, this makes it possible for users to borrow books more than one book
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # The @property decorator below, allow this function(is_overdue) to be called directly from templates
    # Note: First verify whether due_back is empty before making a comparison. An empty due_back field
    # would cause Django to throw an error instead of showing the page: empty values are not comparable.
    # This is not something site users should experience!
    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    class Meta:
        ordering = ['due_back']

        # Permissions are associated with models and define the operations that
        # can be performed on a model instance by a user who has the permission.
        # By default, Django automatically gives add, change, and delete permissions
        # to all models, which allow users with the permissions to perform the
        # associated actions via the admin site. Testing on permissions in views and
        # templates is then very similar for testing on the authentication status
        # (and in fact, testing for a permission also tests for authentication).

        # Defining permissions is done on the model "class Meta" section, using the
        # permissions field. You can specify as many permissions as you need in a tuple,
        # each permission itself being defined in a nested tuple containing the permission
        # name and permission display value.

        permissions = (
            ("can_mark_returned", "Set book as returned"),
            ("can_renew", "Renew date for books on loan"),
            ("can_borrow", "Users can make a borrow request"),
        )

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('catalog:bookinstance_list')

    def __str__(self):
        return '{0} ({1})'.format(self.id, self.book.title)


class AuthorManager(models.Manager):
    """This model handles every search query for the Author Model"""
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = (Q(first_name__icontains=query) |
                         Q(last_name__icontains=query)
                         )
            qs = qs.filter(or_lookup).distinct()
        return qs


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True, help_text='yyyy-mm-dd')
    date_of_death = models.DateField('died', null=True, blank=True)

    objects = AuthorManager()

    class Meta:
        ordering = ['last_name', 'first_name']

    # This is here to ensure a CreateView/UpdateView in views.py and on the html page has
    # a redirect url on Create/Update Submit Button
    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('catalog:author-detail', args=[str(self.id)])

    def __str__(self):
        return '{0}, {1}'.format(self.last_name, self.first_name)
