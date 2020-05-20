from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'catalog'
urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),
    path('book/<uuid:pk>/renew', views.renew_book_librarian, name='renew-book-librarian'),

]


# Author forms created in views
urlpatterns += [
    path('authors/create/', views.AuthorCreateView.as_view(), name='author_create'),
    path('authors/<int:pk>/update/', views.AuthorUpdateView.as_view(), name='author_update'),
    path('authors/<int:pk>/delete/', views.AuthorDeleteView.as_view(), name='author_delete'),

    path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),

    path('genres/create/', views.GenreCreateView.as_view(), name='genre_create'),
    path('languages/create/', views.LanguageCreateView.as_view(), name='language_create'),
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
    path('languages/', views.LanguageListView.as_view(), name='language_list'),
    path('genres/<int:pk>/delete/', views.GenreDeleteView.as_view(), name='genre_delete'),
    path('languages/<int:pk>/delete/', views.LanguageDeleteView.as_view(), name='language_delete'),

    path('bookcopy/create/', views.BookInstanceCreateView.as_view(), name='bookinstance_create'),
    path('bookcopy/update/<uuid:pk>', views.BookInstanceUpdateView.as_view(), name='bookinstance_update'),
    path('bookcopy/<uuid:pk>/delete/', views.BookInstanceDeleteView.as_view(), name='bookinstance_delete'),
    path('bookcopy/', views.BookInstanceListView.as_view(), name='bookinstance_list'),
    path('available/', views.BookInstanceAvailableView.as_view(), name='copy_available'),

    path('available/<uuid:pk>/borrow/', views.borrow_book, name='borrow_request'),
    path('approve_borrow/', views.BorrowBooksAllRequestListView.as_view(), name='borrow_approval_list'),
    path('bookcopy/approve/<uuid:pk>/', views.book_instance_approve, name='copy_approve'),
    path('bookcopy/mark_return/<uuid:pk>', views.BookInstanceMarkReturnUpdateView.as_view(), name='bookinstance_return'),

    path('accounts/signup/', views.SignUpView.as_view(), name='signup'),
    path('accounts/confirm-email/<str:user_id>/<str:token>/', views.ConfirmRegistration.as_view(), name='confirm_email'),
    path('accounts/signup-redirect/', TemplateView.as_view(template_name='catalog/signup_redirect.html')),
    path('accounts/signup-complete/', TemplateView.as_view(template_name='catalog/signup_complete_after_confirm_email.html'))

]
