import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

# As this file is within the 'catalog' (Django application) folder 
# of the 'locallibrary' (Django project) folder, it makes no difference
# wether the "package" name 'catalog' is prepended or not:
from .models import Book, Author, BookInstance, Genre # Models of the app
from catalog.forms import RenewBookForm               # Forms  of the app


# Create your views here.


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Challenge: Generate counts for genres and books 
    # that contain a particular word (case insensitive)
    num_genres_børn = Genre.objects.filter(name__icontains = "aloud").count()
    num_books_php = Book.objects.filter(title__icontains = "Php").count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres_børn': num_genres_børn,
        'num_books_php': num_books_php,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

# Class-based views
class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

# HTTP 302 eller 403? Se https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication#views
class LoanedBooksByLibrarianListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to Librarian."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_librarian.html'
    paginate_by = 10
    permission_required = 'catalog.can_identify_borrower'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


@login_required # Giver HTTP 403 hvis den mangler, ellers REDIRECT
# https://docs.djangoproject.com/en/3.2/topics/auth/default/#the-login-required-decorator
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        proposed_renewal_date = datetime.date.today()+datetime.timedelta(weeks=3.0)
        form = RenewBookForm(request.POST,initial={'due_back': proposed_renewal_date})

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['due_back'] # form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)



from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

#@login_required
#@permission_required('catalog.can_mark_returned', raise_exception=True)
class AuthorCreate(LoginRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(LoginRequiredMixin, UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    permission_required='catalog.can_mark_returned'

class AuthorDelete(LoginRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required='catalog.can_mark_returned'

###
class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    permission_required='catalog.can_mark_returned'

class BookDelete(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required='catalog.can_mark_returned'
