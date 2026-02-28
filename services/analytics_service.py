from database.models import Test
from database.db import db

def get_progress_data():
    tests = Test.query.order_by(Test.created_at).all()
    return [
        {
            "date": t.created_at.strftime("%Y-%m-%d"),
            "percentage": t.percentage
        }
        for t in tests
    ]