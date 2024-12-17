from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer
from django.contrib.auth.models import User


class AuthorAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        
        self.client.force_authenticate(user=self.user)
        
        self.author1 = Author.objects.create(
            name='George Orwell', 
            bio='Famous dystopian novelist'
        )
        self.author2 = Author.objects.create(
            name='Jane Austen', 
            bio='Renowned romantic fiction writer'
        )
        
        self.valid_payload = {
            'name': 'Ernest Hemingway',
            'bio': 'Nobel Prize-winning author'
        }
        
        self.invalid_payload = {
            'name': '',
        }

    def test_get_all_authors(self):
        response = self.client.get(reverse('author-list'))
        
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_valid_author(self):
        response = self.client.post(
            reverse('author-list'), 
            self.valid_payload
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Author.objects.filter(name='Ernest Hemingway').exists())

    def test_create_invalid_author(self):
        response = self.client.post(
            reverse('author-list'), 
            self.invalid_payload
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_valid_single_author(self):
        response = self.client.get(
            reverse('author-detail', kwargs={'pk': self.author1.pk})
        )
        
        serializer = AuthorSerializer(self.author1)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_author(self):
        update_payload = {
            'name': 'George Orwell Updated',
            'bio': 'Updated bio for Orwell'
        }
        
        response = self.client.put(
            reverse('author-detail', kwargs={'pk': self.author1.pk}),
            update_payload
        )
        
        self.author1.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.author1.name, 'George Orwell Updated')
        self.assertEqual(self.author1.bio, 'Updated bio for Orwell')


class BookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )
        
        self.client.force_authenticate(user=self.user)
        
        self.author = Author.objects.create(
            name='Test Author', 
            bio='Test Bio'
        )
        
        self.book1 = Book.objects.create(
            title='1984', 
            author=self.author, 
            isbn='1234567890123',
            available_copies=5
        )
        self.book2 = Book.objects.create(
            title='Animal Farm', 
            author=self.author, 
            isbn='9876543210987',
            available_copies=3
        )
        
        self.valid_payload = {
            'title': 'New Book',
            'author': self.author.id,
            'isbn': '1111222233334',
            'available_copies': 10
        }
        
        self.invalid_payload = {
            'title': '',
            'author': self.author.id,
            'isbn': '1111222233334'
        }

    def test_get_all_books(self):
        response = self.client.get(reverse('book-list'))
        
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_valid_book(self):
        response = self.client.post(
            reverse('book-list'), 
            self.valid_payload
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title='New Book').exists())

    def test_create_book_with_duplicate_isbn(self):
        duplicate_payload = self.valid_payload.copy()
        duplicate_payload['isbn'] = self.book1.isbn
        
        response = self.client.post(
            reverse('book-list'), 
            duplicate_payload
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_book_available_copies(self):
        update_payload = {
            'title': self.book1.title,
            'author': self.book1.author.id,
            'isbn': self.book1.isbn,
            'available_copies': 10
        }
        
        response = self.client.put(
            reverse('book-detail', kwargs={'pk': self.book1.pk}),
            update_payload
        )
        
        self.book1.refresh_from_db()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book1.available_copies, 10)