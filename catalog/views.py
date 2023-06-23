import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import RenewBookForm
from .models import Book, Author, BookInstance, Genre

#  path('', index, name='index')


def index(request):
    num_authors = Author.objects.count()
    num_books = Book.objects.all().count()
    num_bookinstances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        "num_books": num_books,
        "num_bookinstances": num_bookinstances,
        'num_instances_available': num_instances_available,
        "num_authors": num_authors,
        'num_visits': num_visits
    }
    return render(request, 'catalog/index.html', context)


class MyView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'


@ login_required
@ permission_required('catalog.can_mark_returned', raise_exception=True)
def my_view(request):
    return HttpResponse('inside views.my-view')


class MyView(PermissionRequiredMixin, View):
    permission_required = 'catalog.can_mark_returned'
    # Or multiple permissions
    # , 'catalog.can_edit')
    permission_required = ('catalog.can_mark_returned')
    # Note that 'catalog.can_edit' is just an example
    # the catalog application doesn't have such permission!

# path('books/', BookListView.as_view(), name='books'),


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    print('inside views.BookListView')
    # num_authors = Author.objects.count()
    num_books = Book.objects.all().count()
    print('num_books ', num_books)
    context_object_name = 'book_list'
    print('book_list is ', context_object_name)
    # queryset = Book.objects.filter(title__icontains='Title5')[
    #    :5]  # Get 5 books containing the title war
    template_name = 'catalog/book_list.html'

# path('book/<int:pk>', BookDetailView.as_view(), name='book-detail'),
# re_path(r'^book/(?P<pk>\d+)$', BookDetailView.as_view(), name='book-detail'),


class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, primary_key):
        try:
            book = Book.objects.get(pk=primary_key)
        except Book.DoesNotExist:
            raise Http404('Book does not exist')

        return render(request, 'catalog/book_detail.html', context={'book': book})

    '''
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context
    '''
    '''
    def get_queryset(self):

        queryset = Book.objects.filter(title__icontains='Title4')[:5]

        # Get 5 books containing the title war
        return queryset
    '''

#   path('borrowed/', borrowed, name='borrowed'),


def borrowed(request):
    bookinstance_list = BookInstance.objects.filter(status__exact='o')
    context = {
        'bookinstance_list': bookinstance_list
    }
    return render(request, 'catalog/borrowed.html', context)


# path('mybooks/', LoanedBooksByUserListView.as_view(), name='my-borrowed'),
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

#  path('book/<uuid:pk>/renew/', renew_book_librarian,
#  name='renew-book-librarian'),


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):

    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':   # If this is a POST request then process the Form data

        # Create form instance - populate it with data from the request (binding):
        form = RenewBookForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('borrowed'))

    else:  # If this is a GET (or any other method) create the default form.
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

# path('authors/', AuthorListView.as_view(), name='authors'),


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
    # num_authors = Author.objects.count()
    num_authors = Author.objects.all().count()
    context_object_name = 'author_list'
    # queryset = Author.objects.filter(title__icontains='????')[
    #    :5]  # Get 5 authors containing the title war
    template_name = 'catalog/author_list.html'

# path('author/<int:pk>', AuthorDetailView.as_view(), name='author-detail'),
# re_path(r'^author/(?P<pk>\d+)$, AuthorDetailView.as_view(), name='author-detail'),


class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, primary_key):
        try:
            author = Author.objects.get(pk=primary_key)
        except Author.DoesNotExist:
            raise Http404('Author does not exist')

        return render(request, 'catalog/author_detail.html', context={'author': author})
        # return HttpResponse('from inside author_detail_view')

# path('author/create/', AuthorCreate.as_view(), name='author-create'),


class AuthorCreate(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}

#  path('author/<int:pk>/update/', AuthorUpdate.as_view(), name='author-update'),


class AuthorUpdate(UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'

# path('author/<int:pk>/delete/', AuthorDelete.as_view(), name='author-delete'),


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


# path('author/create/', AuthorCreate.as_view(), name='author-create'),

class BookCreate(CreateView):
    print('ln 191 inside views.UserCreate')
    model = Book
    fields = '__all__'

# path('author/<int:pk>/update/', AuthorUpdate.as_view(), name='author-update'),


class BookUpdate(UpdateView):
    model = Book
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'

# path('author/<int:pk>/delete/', AuthorDelete.as_view(), name='author-delete'),


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
