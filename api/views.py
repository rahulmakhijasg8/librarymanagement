from .models import Book, BorrowRecord, Author
from rest_framework.viewsets import ModelViewSet, ViewSet
from .serializers import AuthorSerializer, BookSerializer, BorrowRecordSerializer, UserRegistrationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
import os, json
from .tasks import generate_library_report
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
    

class BookViewSet(ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.select_related('author').all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post','get','put','delete']

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return Response({"detail": "PATCH method is not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
    

class BorrowRecordViewSet(ModelViewSet):
    serializer_class = BorrowRecordSerializer
    queryset = BorrowRecord.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        copies = serializer.validated_data['book'].available_copies
        if copies < 1:
            return Response({'details':'No Copies available for the requested book.'})
        serializer.validated_data['book'].available_copies = copies - 1
        serializer.validated_data['book'].save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['put'], url_path='return')
    def return_book(self, request, pk=None):
        if not self.get_object().return_date:
            self.get_object().return_date = timezone.now()
            self.get_object().save()
            book = self.get_object().book
            book.available_copies += 1
            book.save()
            return Response({"status": "book borrowed"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Book already returned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class ReportViewSet(ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the latest library report",
        responses={
            200: openapi.Response(
                description='Latest library report',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_authors': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_books': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_borrowed_books': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'timestamp': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )

    def list(self, request):
        reports_dir = 'reports/'
        if [os.path.join(reports_dir, f) for f in os.listdir(reports_dir)]:
            latest_report = max(
                [os.path.join(reports_dir, f) for f in os.listdir(reports_dir)],
                key=os.path.getctime
            )
            
            with open(latest_report, 'r') as f:
                report = json.load(f)
            
            return Response(report)
        return Response({'Detail': 'No borrow report exists.'})
    
    @swagger_auto_schema(
        operation_description="Generate a new library report in the background",
        responses={
            200: openapi.Response(
                description='Report generation started',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )

    def create(self, request, *args, **kwargs):
        task = generate_library_report.delay()
        return Response({
            'task_id': task.id,
            'message': 'Report generation started'
        })


user_registration_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=['username', 'email', 'password']
)

class UserRegistrationView(ViewSet):
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        operation_description="Create a new user with a username, email, and password.",
        request_body=user_registration_request_body,
        responses={
            200: openapi.Response(
                description='User created.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING   )
                    }
                )
            )
        }
    )

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'username': user.username,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)