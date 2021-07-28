from django.contrib import admin
from .models import Author, Genre, Book, BookInstance

# Instead of the default admin views presented here, we modify:
# admin.site.register(Book)
# admin.site.register(Author)
# admin.site.register(BookInstance)

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance

# The following DECORATED ModelAdmin subclasses are an alternative way to declare compared to Author above.
# Register the Admin classes for Book using the decorator
# inlines - Related BookInstance records shown with Book
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book','imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back','borrower')
        }),
    )

# Directly from import - no modifications
admin.site.register(Genre)
