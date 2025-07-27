# Crypto Groot

A Django-based cryptocurrency analytics and trading dashboard with user management, subscription plans, payments, usage logging, watchlists, and real-time trading indicators.

## Features
- Custom user model for authentication
- Subscription plans and payment tracking
- User usage logging
- Watchlist (saved symbols) per user
- Real-time trading dashboard (Django Plotly Dash)
- Django admin integration
- REST API for all major models
- Management commands for automation
- Comprehensive test suite

## Setup

### 1. Clone the repository
```
git clone <repo-url>
cd Crypto-Groot
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Apply migrations
```
python manage.py makemigrations
python manage.py migrate
```

### 4. Create a superuser
```
python manage.py createsuperuser
```

### 5. (Optional) Create default subscription plans
```
python manage.py create_subscription_plans
```

### 6. Run the development server
```
python manage.py runserver
```

## Models

### User
Custom user model (email unique, extends AbstractUser).

### SubscriptionPlan
- name, price, duration_days, description, is_active

### Payment
- user, plan, amount, timestamp, status, transaction_id

### UserUsageLog
- user, action, timestamp, details

### Watchlist
- user, symbol, added_at

## Admin
All models are registered in the Django admin for easy management.

## Views & Templates
- Dashboard: `/dashboard/`
- Users: `/users/`
- Subscription Plans: `/plans/`, `/plans/create/`, `/plans/<id>/`
- Payments: `/payments/`
- Usage Logs: `/usage-logs/`
- Watchlist: `/watchlist/`

## REST API
All major models are available via REST API at `/api/`:
- `/api/users/`
- `/api/plans/`
- `/api/payments/`
- `/api/usage-logs/`
- `/api/watchlist/`

## Management Commands
- `create_subscription_plans`: Create default plans
- `create_superuser_with_plan <username> <email> <password> --plan <PlanName>`: Create a superuser and assign a plan
- `log_user_usage <username> <action> --details "optional details"`: Log a user action
- `add_to_watchlist <username> <symbol>`: Add a symbol to a user's watchlist
- `remove_from_watchlist <username> <symbol>`: Remove a symbol from a user's watchlist

## Testing
Run all tests:
```
python manage.py test
```

## Real-Time Dashboard
- Accessible at `/dashboard/` (or via the main page)
- Uses Django Plotly Dash for real-time trading indicators (EMA, RSI, candlestick)
- Data is fetched from Binance and updated live

## Extending
- Add more fields to the user or other models as needed
- Add more API endpoints or permissions
- Add more management commands for automation
- Integrate with payment gateways for real payments

## Production
- Use a production WSGI/ASGI server (e.g., gunicorn, Daphne)
- Set `DEBUG = False` and configure allowed hosts
- Serve static files with a web server (run `python manage.py collectstatic`)

## License
MIT