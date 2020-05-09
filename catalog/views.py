from django.shortcuts import render
from .models import Author, Book, BookInstance, Genre, Language
from django.views import generic


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
