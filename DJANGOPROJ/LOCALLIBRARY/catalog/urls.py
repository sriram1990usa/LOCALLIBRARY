from django.urls import path, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from .views import index, BookListView, BookDetailView, AuthorListView, AuthorDetailView
from .views import borrowed, LoanedBooksByUserListView, renew_book_librarian
from .views import AuthorCreate, AuthorUpdate, AuthorDelete
from .views import BookCreate, BookUpdate, BookDelete

urlpatterns = [
    path('', index, name='index'),
    path('', RedirectView.as_view(url='catalog/', permanent=True)),

    path('books/', BookListView.as_view(), name='books'),
    path('book/<int:pk>', BookDetailView.as_view(), name='book-detail'),
    # re_path(r'^book/(?P<pk>\d+)$', BookDetailView.as_view(), name='book-detail'),
    path('book/create/', BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', BookDelete.as_view(), name='book-delete'),
    path('mybooks/', LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('borrowed/', borrowed, name='borrowed'),
    path('book/<uuid:pk>/renew/', renew_book_librarian,
         name='renew-book-librarian'),

    path('authors/', AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', AuthorDetailView.as_view(), name='author-detail'),
    # re_path(r'^author/(?P<pk>\d+)$, AuthorDetailView.as_view(), name='author-detail'),
    path('author/create/', AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', AuthorDelete.as_view(), name='author-delete'),



]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
