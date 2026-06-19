from calendar import month_name
from datetime import date

from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse

from .models import Income, Loan, Todo


def _cors_json(data, status=200):
    response = JsonResponse(data, safe=isinstance(data, dict), status=status)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def api_dashboard_stats(request):
    if request.method == "OPTIONS":
        return _cors_json({})

    total_income = Income.objects.aggregate(total=Sum('amount'))['total'] or 0
    active_users = User.objects.count()
    total_mentors = Loan.objects.count()

    payload = {
        'totalRevenue': float(total_income),
        'activeUsers': active_users,
        'newUsers': 1457,
        'totalMentors': total_mentors,
        'growth': {
            'revenue': 8.2,
            'activeUsers': 11.7,
            'newUsers': -2.9,
            'mentors': 20.9,
        },
    }
    return _cors_json(payload)


def api_dashboard_revenue(request):
    if request.method == "OPTIONS":
        return _cors_json({})

    month_totals = {month: 0.0 for month in month_name if month}
    income_by_month = (
        Income.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    for row in income_by_month:
        month_key = row['month'].strftime('%B')
        month_totals[month_key] = float(row['total'] or 0)

    months = [month for month in month_name if month]
    data = [month_totals[month] for month in months]

    return _cors_json({
        'months': months,
        'revenue': data,
    })


def api_dashboard_calendar(request):
    if request.method == "OPTIONS":
        return _cors_json({})

    today = date.today()
    selected_day = 19

    events = []
    loans = Loan.objects.filter(due_date__month=today.month)[:4]
    todos = Todo.objects.filter(due_date__month=today.month)[:3]

    for loan in loans:
        if loan.due_date:
            events.append({
                'day': loan.due_date.day,
                'title': f"{loan.person_name} due",
                'type': 'loan',
            })

    for todo in todos:
        if todo.due_date:
            events.append({
                'day': todo.due_date.day,
                'title': todo.title,
                'type': 'task',
            })

    if not events:
        events.append({
            'day': selected_day,
            'title': 'Planning review',
            'type': 'event',
        })

    return _cors_json({
        'month': today.strftime('%B'),
        'year': today.year,
        'selectedDay': selected_day,
        'events': events,
    })


def api_dashboard_community_growth(request):
    if request.method == "OPTIONS":
        return _cors_json({})

    return _cors_json({
        'percentage': 65,
        'trend': 0.91,
        'label': '+0.91% from last month',
    })


def api_course_purchases(request):
    if request.method == "OPTIONS":
        return _cors_json({})

    purchases = [
        {
            'course': 'Digital Marketing',
            'student': 'Aria',
            'studentId': '#3456791',
            'amount': '$372.00',
            'status': 'Paid',
        },
        {
            'course': 'UX Design Fundamentals',
            'student': 'Mia',
            'studentId': '#3456792',
            'amount': '$449.00',
            'status': 'Pending',
        },
        {
            'course': 'Growth Hacking',
            'student': 'Leo',
            'studentId': '#3456793',
            'amount': '$299.00',
            'status': 'Failed',
        },
    ]

    return _cors_json({'purchases': purchases})
