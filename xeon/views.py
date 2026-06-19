from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import get_object_or_404

from .models import Income, Expense, Todo, Loan, Category


def create_default_categories(user):
    default_incomes = ['Salary', 'Freelance', 'Investments', 'Gifts', 'Others']
    default_expenses = [
        'Food & Dining', 'Groceries', 'Rent', 'Utilities', 
        'Transportation', 'Entertainment', 'Medical', 'Shopping', 'Others'
    ]
    if not Category.objects.filter(user=user).exists():
        for name in default_incomes:
            Category.objects.get_or_create(user=user, name=name, type='income')
        for name in default_expenses:
            Category.objects.get_or_create(user=user, name=name, type='expense')


# -----------------------------
# Home
# -----------------------------
def home(request):
    if request.user.is_authenticated:
        return redirect('xeon:dashboard')
    return render(request, 'xeon/home.html')


# -----------------------------
# Auth
# -----------------------------
def login_page(request):
    if request.user.is_authenticated:
        return redirect('xeon:dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user account actually exists
        user_exists = User.objects.filter(username=username).exists()

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            # respect `next` parameter when present
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('xeon:dashboard')
        else:
            if not user_exists:
                messages.error(request, "This account does not exist. Please sign up first.")
            else:
                messages.error(request, "Incorrect password. Please try again.")

    return render(request, 'xeon/login.html')


def register_page(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        first_name = request.POST.get('first_name') or ''
        last_name = request.POST.get('last_name') or ''

        if not username or not password:
            messages.error(request, "Username and password are required")
            return render(request, 'xeon/register.html', {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'xeon/register.html', {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
            })

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, "Account created successfully")
            return redirect('xeon:login_page')
        except Exception as e:
            # Log error to console and show user-friendly message
            print(f"[register_page] error creating user: {e}")
            messages.error(request, "Unable to create account. Please try again.")
            return render(request, 'xeon/register.html', {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
            })

    return render(request, 'xeon/register.html')


def logout_page(request):
    logout(request)
    return redirect('xeon:login_page')


# -----------------------------
# Dashboard
# -----------------------------
@login_required
def dashboard(request):
    user = request.user
    create_default_categories(user)

    # 1. Determine selected date and year
    date_str = request.GET.get('date')
    if date_str:
        try:
            today_date = date.fromisoformat(date_str)
        except ValueError:
            today_date = date.today()
    else:
        # Default to the latest transaction date (or today, whichever is more recent/relevant)
        latest_income = Income.objects.filter(user=user).order_by('-date').first()
        latest_expense = Expense.objects.filter(user=user).order_by('-date').first()
        dates = [date.today()]
        if latest_income:
            dates.append(latest_income.date)
        if latest_expense:
            dates.append(latest_expense.date)
        today_date = max(dates)

    selected_year = today_date.year

    total_income = Income.objects.filter(user=user)\
        .aggregate(Sum('amount'))['amount__sum'] or 0

    total_expense = Expense.objects.filter(user=user)\
        .aggregate(Sum('amount'))['amount__sum'] or 0

    balance = total_income - total_expense

    todos = Todo.objects.filter(user=user).order_by('-created_at')[:5]
    todo_total = Todo.objects.filter(user=user).count()
    todo_completed = Todo.objects.filter(user=user, is_completed=True).count()
    todo_pending = todo_total - todo_completed

    recent_incomes = Income.objects.filter(user=user).order_by('-date')[:4]
    recent_expenses = Expense.objects.filter(user=user).order_by('-date')[:4]
    income_count = Income.objects.filter(user=user).count()
    expense_count = Expense.objects.filter(user=user).count()

    # Filter monthly revenue data by currently selected year
    monthly_income_query = (
        Income.objects.filter(user=user, date__year=selected_year)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    income_by_month = {item['month'].month: item['total'] for item in monthly_income_query if item['month']}
    raw_revenue_data = [
        {'month': label, 'value': income_by_month.get(index + 1, 0)}
        for index, label in enumerate(month_labels)
    ]

    max_revenue_value = max([item['value'] for item in raw_revenue_data] + [1])
    revenue_data = [
        {
            'month': item['month'],
            'value': item['value'],
            'height': 35 + int((item['value'] / max_revenue_value) * 160)
        }
        for item in raw_revenue_data
    ]

    selected_day = today_date.day
    calendar_month = today_date.strftime("%B %Y")
    
    # Generate 5 days centered around selected date
    days_range = [today_date + timedelta(days=i) for i in range(-2, 3)]
    calendar_days = [{'day': d.day, 'date_str': d.isoformat()} for d in days_range]
    weekdays = [d.strftime("%a") for d in days_range]
    
    prev_date = (today_date - timedelta(days=5)).isoformat()
    next_date = (today_date + timedelta(days=5)).isoformat()

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'todos': todos,
        'todo_total': todo_total,
        'todo_completed': todo_completed,
        'todo_pending': todo_pending,
        'income_count': income_count,
        'expense_count': expense_count,
        'recent_incomes': recent_incomes,
        'recent_expenses': recent_expenses,
        'revenue_data': revenue_data,
        'community_growth': 0.91,
        'calendar_month': calendar_month,
        'calendar_days': calendar_days,
        'selected_day': selected_day,
        'weekdays': weekdays,
        'prev_date': prev_date,
        'next_date': next_date,
        'selected_year': selected_year,
    }

    return render(request, 'xeon/dashboard.html', context)

# -----------------------------
# Income
# -----------------------------
@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    return render(request, 'xeon/income.html', {'incomes': incomes})


@login_required
def add_income(request):
    create_default_categories(request.user)
    categories = Category.objects.filter(user=request.user, type='income')
    today = date.today().isoformat()

    if request.method == "POST":
        amount = request.POST.get('amount') or '0'
        date_value = request.POST.get('date') or today
        note = request.POST.get('note') or ''
        payment_method = request.POST.get('payment_method') or 'cash'

        Income.objects.create(
            user=request.user,
            amount=Decimal(amount),
            category_id=request.POST.get('category') or None,
            payment_method=payment_method,
            date=date_value,
            note=note,
        )
        return redirect('xeon:income_list')

    return render(request, 'xeon/add_income.html', {
        'categories': categories,
        'today': today,
    })

@login_required
def delete_income(request, id):
    if request.method == "POST":
        income = get_object_or_404(Income, id=id, user=request.user)
        income.delete()
    return redirect('xeon:income_list')

# -----------------------------
# Expense
# -----------------------------
@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    monthly_expenses = (
        expenses
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('-month')
    )

    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'xeon/expense.html', {
        'expenses': expenses,
        'monthly_expenses': monthly_expenses,
        'total_expense': total_expense
    })


@login_required
def add_expense(request):
    create_default_categories(request.user)
    categories = Category.objects.filter(user=request.user, type='expense')

    if request.method == "POST":
        Expense.objects.create(
            user=request.user,
            amount=request.POST.get('amount') or 0,
            category_id=request.POST.get('category'),
            payment_method=request.POST.get('payment_method'),
            date=request.POST.get('date'),
        )
        return redirect('xeon:expense_list')

    return render(request, 'xeon/add_expense.html', {'categories': categories})


@login_required
def edit_expense(request, id):
    create_default_categories(request.user)
    expense = get_object_or_404(Expense, id=id, user=request.user)
    categories = Category.objects.filter(user=request.user, type='expense')

    if request.method == "POST":
        expense.amount = request.POST.get('amount')
        expense.category_id = request.POST.get('category')
        expense.payment_method = request.POST.get('payment_method')
        expense.date = request.POST.get('date')
        expense.note = request.POST.get('note')
        expense.save()

        return redirect('xeon:expense_list')

    return render(request, 'xeon/edit_expense.html', {
        'expense': expense,
        'categories': categories
    })


@login_required
def delete_expense(request, id):
    if request.method == "POST":
        expense = get_object_or_404(Expense, id=id, user=request.user)
        expense.delete()
    return redirect('xeon:expense_list')


# -----------------------------
# Todo
# -----------------------------
@login_required
def todo_list(request):
    todos = Todo.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'xeon/todo.html', {'todos': todos})


@login_required
def add_todo(request):
    if request.method == "POST":
        Todo.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            priority=request.POST.get('priority'),
            due_date=request.POST.get('due_date') or None,
        )
        return redirect('xeon:todo_list')

    return render(request, 'xeon/add_todo.html')


@login_required
def edit_todo(request, id):
    todo = get_object_or_404(Todo, id=id, user=request.user)

    if request.method == "POST":
        todo.title = request.POST.get('title')
        todo.description = request.POST.get('description')
        todo.priority = request.POST.get('priority')
        todo.due_date = request.POST.get('due_date') or None
        todo.save()

        return redirect('xeon:todo_list')

    return render(request, 'xeon/edit_todo.html', {'todo': todo})


@login_required
def delete_todo(request, id):
    if request.method == "POST":    
        todo = get_object_or_404(Todo, id=id, user=request.user)
        todo.delete()
    return redirect('xeon:todo_list')


# -----------------------------
# Loan
# -----------------------------
@login_required
def loan_list(request):
    loans = Loan.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'xeon/loan.html', {'loans': loans})


@login_required
def add_loan(request):
    if request.method == "POST":
        Loan.objects.create(
            user=request.user,
            person_name=request.POST.get('person_name'),
            loan_type=request.POST.get('loan_type'),
            total_amount=request.POST.get('total_amount') or 0,
            paid_amount=request.POST.get('paid_amount') or 0,
            due_date=request.POST.get('due_date') or None,
            note=request.POST.get('note'),
        )
        return redirect('xeon:loan_list')

    return render(request, 'xeon/add_loan.html')


@login_required
def delete_loan(request, id):
    if request.method == "POST":
        loan = get_object_or_404(Loan, id=id, user=request.user)
        loan.delete()
    return redirect('xeon:loan_list')


@login_required
def edit_loan(request, id):
    loan = get_object_or_404(Loan, id=id, user=request.user)

    if request.method == "POST":
        try:
            loan.person_name = request.POST.get('person_name')
            loan.loan_type = request.POST.get('loan_type')
            loan.total_amount = float(request.POST.get('total_amount') or 0)
            loan.paid_amount = float(request.POST.get('paid_amount') or 0)
            loan.due_date = request.POST.get('due_date') or None
            loan.note = request.POST.get('note')
            
            # Auto-update status based on payment
            if loan.paid_amount >= loan.total_amount:
                loan.status = 'completed'
            elif loan.paid_amount > 0:
                loan.status = 'partial'
            else:
                loan.status = 'pending'
            
            loan.save()
            messages.success(request, "Loan updated successfully!")
            return redirect('xeon:loan_list')
        except Exception as e:
            messages.error(request, f"Error updating loan: {str(e)}")

    return render(request, 'xeon/edit_loan.html', {'loan': loan})


@login_required
def complete_loan(request, id):
    if request.method == "POST":
        loan = get_object_or_404(Loan, id=id, user=request.user)
        loan.status = 'completed'
        loan.save()
    return redirect('xeon:loan_list')


@login_required
def toggle_todo(request, id):
    todo = get_object_or_404(Todo, id=id, user=request.user)
    todo.is_completed = not todo.is_completed
    todo.save()
    return redirect('xeon:todo_list')

@login_required
def edit_income(request, id):
    create_default_categories(request.user)
    income = get_object_or_404(Income, id=id, user=request.user)
    categories = Category.objects.filter(user=request.user, type='income')

    if request.method == "POST":
        income.amount = request.POST.get('amount')
        income.category_id = request.POST.get('category')
        income.payment_method = request.POST.get('payment_method') or 'cash'
        income.date = request.POST.get('date')
        income.note = request.POST.get('note')
        income.save()

        return redirect('xeon:income_list')

    return render(request, 'xeon/edit_income.html', {
        'income': income,
        'categories': categories
    })


@login_required
def add_category(request):
    next_url = request.GET.get('next')

    if request.method == "POST":
        Category.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            type=request.POST.get('type')
        )

        if next_url:
            return redirect(next_url)

        return redirect('xeon:dashboard')

    return render(request, 'xeon/add_category.html')