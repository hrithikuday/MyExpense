# MyExpense — Smart Financial Tracker

MyExpense is a next-generation personal finance assistant and tracking application built with Django. It provides a unified, clutter-free dashboard to track your income streams, manage daily expenses, structure loans, and maintain daily tasks in one clean and privacy-focused cockpit.

## 🚀 Features

- **📊 Dashboard Overview**: A unified dashboard tracking total balance, monthly income, monthly expenses, recent transactions, and active tasks.
- **💹 Income Streams**: Track multiple income streams categorized by custom rules and mapped to payment methods (Cash, Card, UPI, Bank Transfer).
- **💸 Expense Cockpit**: Log daily expenditures, set custom categories, and monitor where your money goes.
- **🏦 Debt & Lending (Loans)**: Manage borrowed or lent funds, partial payments, outstanding balances, due dates, and payment status (Pending, Partial, Completed).
- **✓ Task Priorities**: Maintain a checklist of financial and general tasks with priority levels (Low, Medium, High).
- **🔒 Privacy First**: Secure user authentication and complete isolation of financial data per account.

---

## 🛠️ Tech Stack

- **Backend Framework**: Django 6.x (Python)
- **Database**: SQLite (default/development), PostgreSQL (production/configurable)
- **Front-end / Styling**: Tailwind CSS, HTML5, Custom pure-CSS dashboard components
- **Static Files Serving**: WhiteNoise (with compression)
- **Configuration**: Python Decouple (Environment variable control)

---

## 💻 Installation & Local Setup

### Prerequisites
- Python 3.10+
- Git

### Step-by-Step Guide

1. **Clone the Repository**
   ```bash
   git clone https://github.com/hrithikuday/MyExpense.git
   cd MyExpense
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python -m venv .venv
   # On Windows (Command Prompt)
   .venv\Scripts\activate
   # On Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r main/requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the `main` directory:
   ```env
   SECRET_KEY=your-django-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Run Database Migrations**
   ```bash
   cd main
   python manage.py migrate
   ```

6. **Create a Superuser (Optional, for admin dashboard access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://127.0.0.1:8000`.

---

## 🌐 Production Deployment

The project is pre-configured for hosting on platforms like **Render**.

### Configuration Files
- **`render.yaml`**: Outlines the web service and managed PostgreSQL database service setup.
- **`Procfile`**: Specifies the command to start the gunicorn production server.
- **`runtime.txt`**: Specifies the Python runtime version.

### Production Environment Variables
When deploying to production, make sure to configure:
- `SECRET_KEY`: A strong, random key.
- `DEBUG`: Set to `False`.
- `ALLOWED_HOSTS`: comma-separated allowed hostnames (e.g., `myexpense.hrithikuday.me`).
- `DATABASE_URL`: Connection string for PostgreSQL database.
