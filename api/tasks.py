from celery import shared_task
from .models import Author, Book, BorrowRecord
import json
from datetime import datetime

@shared_task
def generate_library_report():
    report = {
        'total_authors': Author.objects.count(),
        'total_books': Book.objects.count(),
        'total_borrowed_books': BorrowRecord.objects.filter(return_date__isnull=True).count(),
        'timestamp': datetime.now().isoformat()
    }
    
    filename = f'reports/report_{datetime.now().strftime("%Y%m%d")}.json'

    with open(filename, 'w') as f:
        json.dump(report, f)

    return report