from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.PROTECT)
    isbn = models.CharField(max_length=13, unique=True)
    available_copies = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_by = models.CharField(max_length=255)
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateField(null=True)
