import datetime

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.conf import settings
from .models import Author, Book, BookInstance, Genre, Language
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from .forms import LibrarianRenewBookModelForm, LibrarianCreateBookCopyModelForm, \
    LibrarianUpdateBookCopyModelForm, UserBorrowBookModelForm, LibrarianApproveBookCopyBorrowModelForm, \
    LibrarianMarkBookCopyAsReturnedModelForm, SignupForm
from .tokens import user_tokenizer
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage
from django.views import View

from django.contrib.auth.decorators import permission_required, login_required


# Create your views here.
class SignUpView(View):
    """This handles the signup logic for the page"""
    def get(self, request):
        """This function handles the get request for signup"""
        return render(request, 'catalog/signup.html', {'form': SignupForm()})

    def post(self, request):
        """This function handles the post request for signup"""
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_valid = False
            user.is_active = False
            user.save()
            token = user_tokenizer.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            url = 'http://localhost:8000' + reverse(
                'catalog:confirm_email', kwargs={'user_id': uid, 'token': token})
            message = get_template('catalog/signup_confirm_email.html').render({
                'confirm_url': url, 'user': user,
            })
            mail = EmailMessage("Joels' Local Library Email Confirmation", message,
                                to=[user.email], from_email=settings.EMAIL_HOST_USER)
            mail.content_subtype = 'html'
            mail.send()

            return render(request, 'catalog/signup_redirect.html', {'user': user})
        return render(request, 'catalog/signup.html', {'form': form})


class ConfirmRegistrationView(View):
    def get(self, request, user_id, token):
        """This function accounts for failure for when token authentication fails"""
        uid = force_bytes(urlsafe_base64_decode(user_id))
        user = User.objects.get(pk=uid)
        context = {
            'form': SignupForm(),
            'message': 'Registration confirmation error. Please click the reset '
                       'password to generate a new confirmation email.'
        }

        # Checking for authentication is successful
        if user is not None and user_tokenizer.check_token(user, token):
            user.is_valid = True
            user.is_active = True
            user.save()

            # Automatically migrating all authenticated users as Library Member
            # group on signup confirmation.
            group = Group.objects.get(name='Library Members')
            users = User.objects.all()
            for user in users:
                if user.is_active:
                    group.user_set.add(user)
            return render(request, 'catalog/signup_complete_after_confirm_email.html', {'user': user})

        return render(request, 'registration/login.html', context)


def index(request):
    """This function handles the homepage"""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available book (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()
    num_genres = Genre.objects.values_list('name', flat=True).distinct().count()
    num_language = Language.objects.count()

    # Implementing Number of visits to this view(index) as counted in the session variable.
    # The session attribute is a dictionary-like object that you can read and write
    # as many times as you like in your view, modifying it as wished. You can do all
    # the normal dictionary operations, including clearing all data, testing if a key
    # is present, looping through data, etc. Most of the time though, you'll just use
    # the standard "dictionary" API to get and set values.

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_language': num_language,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context)


# Class based views automatically look for templates names in:
# /Project_folder/App_Folder/templates/created_same_app_name_folder/<template_name>.html
# Default context name for this next view is 'the_model_name_list' e.g book_list, but you can
# override it with your own custom name by calling on the 'context_object_name.
# Default template name would be 'the_model_name_list.html', but you can also override it
# as I did with the template_name attribute.

# Django has excellent inbuilt support for pagination. Even better, this is built into the
# generic class-based LIST views so you don't have to do very much to enable it! Just call
# the 'paginate_by' attribute and assign the numbers you want.
class BookListView(generic.ListView):
    """This view list all books in the library"""
    model = Book
    context_object_name = 'list_of_books'
    template_name = 'catalog/book.html'
    paginate_by = 9


# Default context name for this view is 'the_model_name' in small letters e.g book,
# but you can override it with your own custom name by calling on the 'context_object_name.
# Default template name would be 'the_model_name_detail.html', but you can also override it
# with the template_name attribute. I am using the default values here
class BookDetailView(generic.DetailView):
    """This view gives the detail about a specific book in the library"""
    model = Book


"""Function based representation of the above class BookDetailView"""
"""
from django.shortcuts import get_object_or_404

def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)
    return render(request, 'catalog/book_detail.html', context={'book': book})
"""


class BookCreateView(PermissionRequiredMixin, CreateView):
    """This view allows the librarian to add a book to the library"""
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookUpdateView(PermissionRequiredMixin, UpdateView):
    """This view allows the librarian to be able to update already added book in the library"""
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class BookDeleteView(PermissionRequiredMixin, DeleteView):
    """This view allows the librarian to delete a book already added in the library"""
    model = Book
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('catalog:book-list')


# Using the default template name(author_list.html) as well as context name{{author_list}} here
class AuthorListView(generic.ListView):
    """This view gives a list of all the authors in the library"""
    model = Author
    paginate_by = 9


# Using the default template name(author_detail.html) as well as context name{{author}} here
class AuthorDetailView(generic.DetailView):
    """This view gives a specific detail about an author"""
    model = Author


# In this section, we're going to use generic editing views to create pages to add functionality
# to create, edit, and delete Author records from our library — effectively providing a basic
# reimplementation of parts of the Admin site

# For the "create" and "update" cases you need to specify the fields to display in
# the form (using the same syntax as for ModelForm).

# These views will redirect on success to a page specified by [def_get_absolute_url] declared in models.py
# for the particular table being referenced. You can specify an alternative redirect location by explicitly
# declaring parameter success_url (as done for the AuthorDelete class).
# NOTE: success_url seems to only work for delete, failed to work for the other views.
class AuthorCreateView(PermissionRequiredMixin, CreateView):
    """This view allows the librarian to add author to the library"""
    model = Author
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

    # if you want to specify initial value for any field,
    # initial = {'date_of_death': '15/05/2020'}


# TEMPLATES: The "create" and "update" views use the same template by default, which
# will be named after your model: model_name_form.html e.g author_form.html
class AuthorUpdateView(PermissionRequiredMixin, UpdateView):
    """This view allows the librarian to update an already added author in the library"""
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


# TEMPLATES: The "delete" view expects to find a template named with the format
# model_name_confirm_delete.html e.g author_confirm_delete.html
# DeleteView has no default redirect, so we have to manually provide a redirect
class AuthorDeleteView(PermissionRequiredMixin, DeleteView):
    """This view allows the librarian to delete an author already added in the library"""
    model = Author
    permission_required = 'catalog.can_mark_returned'

    # we use the reverse_lazy() function to redirect to our author list after
    # an author has been deleted. It is used instead of reverse because we
    # are providing a URL to a class-based view attribute
    success_url = reverse_lazy('catalog:author-list')


# You can get information about the currently logged in user in templates with the {{ user }}
# template variable (this is added to the template context by default when you set up the
# project. Typically you will first test against the {{ user.is_authenticated }} template
# variable to determine whether the user is eligible to see specific content. To demonstrate
# this, next i'll update our sidebar to display a "Login" link if the user is logged out, and
# a "Logout" link if they are logged in. in 'base.html' Note also how I appended ?next={{request.path}}
# to the end of the URLs, what this does is, after the user has successfully logged in/out,
# the views will use this "next" value to redirect the user back to the page where they first
# clicked the login/logout link


# The easiest way to restrict access to logged-in users in your class-based views is to derive from
# LoginRequiredMixin

# from django.contrib.auth.mixins import LoginRequiredMixin
# class MyView(LoginRequiredMixin, View):
#     login_url = '/login/'
#     redirect_field_name = 'redirect_to'


# view for getting the list of all books that have been loaned to the current user
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance

    # Using a different template_name, rather than using the default, because we may end
    # up having a few different lists of BookInstance records, with different views and
    # templates.

    template_name = 'catalog/user_list_of_book_copies_borrowed.html'
    paginate_by = 10

    # In order to restrict query to just the BookInstance objects for the current user,
    # I re-implement get_queryset() as below. Note that "o" is the stored code for "on loan"
    # and I order by the due_back date so that the oldest items are displayed first.
    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower=self.request.user).filter(
            status__exact='o').order_by(
            'due_back')


# TEMPLATE: The current user's permissions are stored in a template variable called {{ perms }}.
# One can check whether the current user has a particular permission using the specific variable
# name within the associated Django "app" — e.g. {{ perms.catalog.can_mark_returned }}
# ==> ([can_marked_returned] was define in models.py) will be True if the user has this permission,
# and False otherwise. We typically test for the permission using the template {% if %}


# VIEWS: Permissions can be tested in function view using the permission_required decorator or in a
# class-based view using the PermissionRequiredMixin.


# FUNCTION based view with two hypothetical permissions declared in models.py
# from django.contrib.auth.decorators import permission_required
# @permission_required('catalog.can_mark_returned')
# @permission_required('catalog.can_edit')
# def my_view(request):
#     ...


# CLASS based view with two hypothetical permissions declared in models.py
# from django.contrib.auth.mixins import PermissionRequiredMixin
# class MyView(PermissionRequiredMixin, View):
#    permission_required = 'catalog.can_mark_returned'

# Or multiple permissions
#    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')


# To restrict a particular view to only librarians aka staff alone, can be
# achieved using the @staff_member_required for function view or use the
# PermissionRequiredMixin for class views with the common default template
# variable called {{user.is_staff}}


# To test this permission locally, don't forget to give your librarian a 'staff'
# and 'Set Book as returned' permissions from admin.
class AllLoanedBooksLibrarianListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/librarian_all_book_copies_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


# the view has to render the default form when it is first called and then either re-render
# it with error messages if the data is invalid, or process the data and redirect to a new
# page if the data is valid. In order to perform these different actions, the view has to be
# able to know whether it is being called for the first time to render the default form, or
# a subsequent time to validate data.

# For forms that use a POST request to submit information to the server, the most common
# pattern is for the view to test against the POST request type (if request.method == 'POST':)
# to identify form validation requests and GET (using an else condition) to identify the
# initial form creation request.

@permission_required('catalog.can_borrow')
def user_borrow_book(request, pk):
    """This function enables the user to make a borrow book request"""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
        form = UserBorrowBookModelForm(request.POST, request.FILES)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.borrower = request.user
            book_instance.save()
            return render(request, 'catalog/user_book_copies_available.html')
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=2)
        form = UserBorrowBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/user_make_book_copy_borrow_request.html', context)


class BorrowBooksRequestForLibrarianListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books request for borrow by users. Only visible to
    users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/librarian_book_copy_borrow_approval_page.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='a').filter(due_back__isnull=False)


@permission_required('catalog.can_renew')
def librarian_renew_book(request, pk):
    """This function allows the librarian to extend the date for a book copy whose return date is exceeded"""
    # get_object_or_404() Returns a specified object from a model based on its primary key value,
    # and raises an Http404 exception (not found) if the record does not exist.
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form Data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request(binding)
        # Dont forget to change to RenewBook form when using (forms.Form)
        form = LibrarianRenewBookModelForm(request.POST)

        # Check if form is valid
        if form.is_valid():
            # If using (forms.form) from forms.py use: the current active one is for (ModelForm)
            # book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URl. reverse() generates a URL from a URL
            # configuration name and a set of arguments. It is the Python
            # equivalent of the url tag in templates.
            return render(request, 'catalog/librarian_all_book_copies_borrowed.html')

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=1)
        # Dont forget to change to RenewBook form when using (forms.Form)
        # also change {initial} key to 'renewed_date'
        form = LibrarianRenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/librarian_renew_book_copy.html', context)


# Generic Editing Views(FORMS)
# The form handling algorithm we used in our function view example above represents an extremely
# common pattern in form editing views. Django abstracts much of this "boilerplate", by creating
# generic editing views for creating, editing, and deleting views based on models. Not only do
# these handle the "view" behavior, but they automatically create the form class (a ModelForm)
# for you from the model.
#
# CHECK: FormView(which lies somewhere between our function view and the generic views in
# terms of "flexibility" vs "coding effort". Using FormView, you still need to create your Form,
# but you don't have to implement all of the standard form-handling patterns. Instead, you just
# have to provide an implementation of the function that will be called once the submission is
# known to be valid)


class GenreCreateView(PermissionRequiredMixin, CreateView):
    """This view allows the librarian to add a genre that would be attached to a book on creation in the library"""
    model = Genre
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class LanguageCreateView(PermissionRequiredMixin, CreateView):
    """This view allows the librarian to add a book language to the library"""
    model = Language
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class GenreListView(PermissionRequiredMixin, generic.ListView):
    """This view lists all the available genre in te library"""
    model = Genre
    paginate_by = 9
    permission_required = 'catalog.can_mark_returned'


class LanguageListView(PermissionRequiredMixin, generic.ListView):
    """This view lists all the language already added in the library"""
    model = Language
    paginate_by = 9
    permission_required = 'catalog.can_mark_returned'


class GenreDeleteView(PermissionRequiredMixin, DeleteView):
    """This view allows the librarian to delete a book genre already added in the library"""
    model = Genre
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('catalog:genre_list')


class LanguageDeleteView(PermissionRequiredMixin, DeleteView):
    """This view allows the librarian to delete a book language already added in the library"""
    model = Language
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('catalog:language_list')


# id field has been disabled from forms.py, all the necessary fields has been declared there
class CopyOfBookCreateView(PermissionRequiredMixin, CreateView):
    """This view allows the librarian to add many copies of one book to the library catalogue"""
    form_class = LibrarianCreateBookCopyModelForm
    template_name = 'catalog/bookinstance_form.html'
    permission_required = 'catalog.can_mark_returned'


class CopyOfBookUpdateView(PermissionRequiredMixin, UpdateView):
    """This view allows the librarian to update a copy of a particular book already added in the library"""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    form_class = LibrarianUpdateBookCopyModelForm
    template_name = 'catalog/librarian_update_copy_of_book.html'


@permission_required('catalog.can_renew')
def librarian_approve_borrow_request(request, pk):
    """This function allows the librarian to approve a borrow request from the user"""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
        form = LibrarianApproveBookCopyBorrowModelForm(request.POST)
        if form.is_valid():
            book_instance.status = form.cleaned_data['status']
            book_instance.save()
            return render(request, 'catalog/librarian_book_copy_borrow_approval_page.html')
    else:
        form = LibrarianApproveBookCopyBorrowModelForm(initial={'status': 'a'})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/librarian_approve_borrow.html', context)


class CopyOfBookDeleteView(PermissionRequiredMixin, DeleteView):
    """This view deletes a copy of a book fromm the library"""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('catalog:bookinstance_list')


class CopyOfBookListView(PermissionRequiredMixin, generic.ListView):
    """This view lists all the added copy of every book in the library"""
    model = BookInstance
    paginate_by = 6
    permission_required = 'catalog.can_mark_returned'


class CopyOfBookAvailableView(LoginRequiredMixin, generic.ListView):
    """This view list all the copies of book available for borrow for the user"""
    model = BookInstance
    paginate_by = 6
    template_name = 'catalog/user_book_copies_available.html'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='a').filter(due_back__isnull=True)


class LibrarianMarkCopyAsReturnedView(PermissionRequiredMixin, UpdateView):
    """This view allows the librarian to mark a book as returned from the user and makes that copy
    available for borrow again"""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    form_class = LibrarianMarkBookCopyAsReturnedModelForm
    template_name = 'catalog/librarian_book_copy_mark_return.html'


class SearchListView(generic.ListView):
    template_name = 'catalog/book_search.html'
    paginate_by = 15
    count = 0

    def get_queryset(self):
        query = self.request.GET.get('q')
        object_list = Book.objects.filter(
            Q(title__icontains=query)
        )
        return object_list
