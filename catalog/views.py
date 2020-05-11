import datetime

from django.shortcuts import render, get_object_or_404
from .models import Author, Book, BookInstance, Genre, Language
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import RenewBookModelForm, RenewBookForm
from django.contrib.auth.decorators import permission_required


# Create your views here.
def index(request):
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
# Default context name for this view is 'the_model_name_list' e.g book_list, but you can
# override it with your own custom name by calling on the 'context_object_name.
# Default template name would be 'the_model_name_list.html', but you can also override it
# as I did with the template_name attribute.

# Django has excellent inbuilt support for pagination. Even better, this is built into the
# generic class-based LIST views so you don't have to do very much to enable it! Just call
# the 'paginate_by' attribute and assign the numbers you want.
class BookListView(generic.ListView):
    model = Book
    context_object_name = 'list_of_books'
    template_name = 'catalog/book.html'
    paginate_by = 18


# Default context name for this view is 'the_model_name' in small letters e.g book,
# but you can override it with your own custom name by calling on the 'context_object_name.
# Default template name would be 'the_model_name_detail.html', but you can also override it
# with the template_name attribute. I am using the default values here
class BookDetailView(generic.DetailView):
    model = Book


"""Function based representation of the above class BookDetailView"""
"""
from django.shortcuts import get_object_or_404

def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)
    return render(request, 'catalog/book_detail.html', context={'book': book})
"""


# Using the default template name(author_list.html) as well as context name{{author_list}} here
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 25


# Using the default template name(author_detail.html) as well as context name{{author}} here
class AuthorDetailView(generic.DetailView):
    model = Author

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
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
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
class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
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


@permission_required('catalog.can_renew')
def renew_book_librarian(request, pk):

    # get_object_or_404() Returns a specified object from a model based on its primary key value,
    # and raises an Http404 exception (not found) if the record does not exist.
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form Data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request(binding)
        # Dont forget to change to RenewBook form when using (forms.Form)
        form = RenewBookModelForm(request.POST)

        # Check if form is valid
        if form.is_valid():
            # If using (forms.form) from forms.py use: the current active one is for (ModelForm)
            # book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URl. reverse() generates a URL from a URL
            # configuration name and a set of arguments. It is the Python
            # equivalent of the url tag in templates
            return HttpResponseRedirect(reverse('catalog:all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        # Dont forget to change to RenewBook form when using (forms.Form)
        # also change {initial} key to 'renewed_date'
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

