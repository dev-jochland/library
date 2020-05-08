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

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_language': num_language,
    }

    return render(request, 'index.html', context)


# Class based views automatically look for templates names in:
# /Project_folder/App_Folder/templates/created_same_app_name_folder/<template_name>.html
class BookListView(generic.ListView):
    model = Book
    context_object_name = 'list_of_books'
    template_name = 'catalog/book.html'
