from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, BookViewSet, BorrowRecordViewSet, ReportViewSet, UserRegistrationView

router = DefaultRouter()
router.register('authors', AuthorViewSet)
router.register('books', BookViewSet)
router.register('borrow', BorrowRecordViewSet)
router.register('reports', ReportViewSet, basename='report')
router.register('register', UserRegistrationView, basename='register')

urlpatterns = router.urls