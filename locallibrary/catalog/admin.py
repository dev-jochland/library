from django.contrib import admin
from .models import Author, Book, BookInstance, Genre, Language

# Register your models here.

# admin.site.register(Author)
# admin.site.register(Book)
# admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Language)


# Define the Admin Class
@admin.register(Author)  # Does the same thing as admin.site.register() syntax
class AuthorAdmin(admin.ModelAdmin):
    # if you want to show more interesting information about each author, you
    # can use list_display attribute to add additional fields to the view.
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')

    # The fields attribute lists just those fields that are to be displayed on the
    # form, in order. Fields are displayed vertically by default, but will display
    # horizontally if you further group them in a tuple (as shown in the "date"
    # fields below).
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]


# Register the admin class with the associated Model.

# If I didn't use the admin decorator above, I could register the class like below:
# admin.site.register(Author, AuthorAdmin)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Unfortunately we can't directly specify the genre field in list_display because it
    # is a ManyToManyField (Django prevents this because there would be a large database
    # access "cost" in doing so). Instead I'll define a display_genre function to get
    # the information as a string (this is the function I've called below).
    list_display = ('title', 'author', 'display_genre', 'language')

    fields = [('title', 'author'), ('isbn', 'language'), 'summary', 'genre', 'book_cover']


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    # To be able to filter which items are displayed based on that model specific field,
    # You do this by listing those fields in the list_filter attribute
    list_filter = ('status', 'due_back')
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    readonly_fields = ('id',)

    # I added "sections" to group related model information within the detail form,
    # using the fieldsets attribute. Each section has its own title (or None, if you don't
    # want a title) and an associated tuple of fields in a dictionary
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )


# Both models below only have one field, so no need to work on the display
# except to register the model only as done below


# it may make sense to have both the book information and information about the
# specific copies i've got on the same detail page, I do this by inline editing
# of associate records. to see this attribute in admin, comment out class
# BookAdmin above

"""
class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInline]
"""
