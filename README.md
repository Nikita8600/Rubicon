# Finova Bank - Django Banking Application

Educational banking management system built with Python, Django and SQLite.

## Included features

- Customer registration/login/logout
- One bank account per customer
- Savings and Current accounts
- Minimum-balance validation
- Deposit
- Withdrawal
- Account-to-account transfer
- Transaction history and references
- One Debit Card + one Credit Card per bank account
- Card payment limit of ₹20,000 per payment and maximum 4 successful card payments per card per day
- Loan application with salary captured at application time
- Admin-only loan approval; a loan can be approved only when loan amount is less than or equal to applicant salary
- Customer support tickets
- Notifications
- Profile management
- Live dashboard balance/notification polling
- Django admin for users, accounts, cards, transactions, loans, tickets and notifications
- Staff-only banking admin dashboard
- Responsive custom styling
- CSRF protection on POST forms
- Atomic money operations using database transactions and row locking

## Demo administrator

After setup:

Username: admin
Password: Admin@12345

Change this password before using the project for anything beyond a classroom/demo environment.

## Windows setup

PowerShell:

    cd C:\Users\Admin\Desktop\Banking
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    cd finova_bank
    python manage.py migrate
    python manage.py setup_demo
    python manage.py runserver

Open:

    http://127.0.0.1:8000/

Admin:

    http://127.0.0.1:8000/admin/

Admin dashboard:

    http://127.0.0.1:8000/bank-admin/

## If PowerShell blocks activation

Run once in PowerShell:

    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Then activate:

    .\venv\Scripts\Activate.ps1

Do not type `Y` as a separate command. If PowerShell asks for confirmation, answer it at the prompt.

## Resetting this classroom database

If this is a fresh project and you want to start again:

    Stop the server with Ctrl+C
    Delete db.sqlite3
    python manage.py migrate
    python manage.py setup_demo

Do not delete the migration files unless you intentionally want to recreate migrations.

## Important

This is an educational simulation, not production banking software. A real banking platform needs additional controls such as MFA, secure secret/key management, encryption, KYC/AML workflows, fraud monitoring, audit logging, payment-network integrations, secure card/token handling, rate limiting, penetration testing and regulatory controls.
