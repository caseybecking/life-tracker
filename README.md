# Life Tracker

A comprehensive life tracking application built with Python FastAPI backend and modern frontend to track various aspects of life including finances, personal data, home maintenance, and more.

## ✨ Features

### 🏦 Financial Tracking
- **Account Management**: Track multiple bank accounts with balances and metadata
- **Transaction Tracking**: Add, edit, and categorize transactions with required spending flags
- **Balance Updates**: Automatic balance tracking with manual update capabilities
- **Financial Overview**: Net worth charts, spending analysis, and recent transactions
- **Account Details**: Individual account pages with transaction history and balance tracking
- **Budget Planning**: Budget tracking and spending analysis
- **Recurring Transactions**: Support for recurring payment tracking

### 🎨 User Interface
- **Dark Mode**: Configurable dark/light theme with persistent settings
- **Responsive Design**: Modern Bootstrap 5 interface with mobile support
- **Modal Dialogs**: Add/edit forms in modal dialogs for better UX
- **Separate Pages**: Individual finance pages (Overview, Accounts, Transactions, Budget, Settings)
- **Interactive Charts**: Chart.js powered financial visualizations
- **Clickable Elements**: Account rows link to detailed views

### ⚙️ Settings & Configuration
- **Theme Management**: Dark/light mode toggle in settings
- **Category Management**: View and manage finance categories
- **Data Management**: Clear all finance data with confirmation
- **User Preferences**: Persistent settings storage

### 🛠️ Development Tools
- **CLI Commands**: Command-line tools for data management
- **Database Utilities**: Clear data, setup categories, example data
- **API Documentation**: Auto-generated FastAPI docs
- **Migration Support**: Alembic database migrations

## 🗄️ Database Structure

The application uses an Entity-Attribute-Value (EAV) model for maximum flexibility:

- **Nouns**: Main categories (Banking, Person, Home, Vehicle, Hockey)
- **Attributes**: Properties of nouns (Transaction, Casey, Garden, 4-Runner)
- **Values**: Specific data points (Category, Weight, Mowing, Fuel_Gallons)
- **Data**: Actual values with metadata (Income, 165, 10-8-2019, 16.516)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 3. Set Up Database
```bash
# Create PostgreSQL database
createdb life_tracker

# Run migrations
alembic upgrade head

# Set up finance categories (optional)
python cli.py setup-categories
```

### 4. Run the Application
```bash
uvicorn app.main:app --reload
```

### 5. Access the Application
- **Main Application**: http://localhost:8000
- **Finance Overview**: http://localhost:8000/finance/overview
- **Finance Accounts**: http://localhost:8000/finance/accounts
- **Finance Transactions**: http://localhost:8000/finance/transactions
- **Finance Settings**: http://localhost:8000/finance/settings
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
life-tracker/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── routers/             # API routes
│   │   ├── __init__.py
│   │   ├── finance.py       # Financial tracking routes
│   │   └── general.py       # General tracking routes
│   └── static/              # Frontend assets
│       ├── css/
│       │   └── style.css    # Custom styles with dark mode
│       ├── js/
│       │   └── app.js       # Frontend JavaScript
│       └── templates/       # HTML templates
│           ├── base.html    # Base template with theme support
│           ├── finance_overview.html
│           ├── finance_accounts.html
│           ├── finance_transactions.html
│           ├── finance_settings.html
│           └── account_details.html
├── alembic/                 # Database migrations
├── cli.py                   # Command-line interface
├── clear_finance_data.py    # Data clearing utility
├── requirements.txt
└── README.md
```

## 🔌 API Endpoints

### Financial Tracking
- `GET /api/finance/accounts` - List all bank accounts
- `POST /api/finance/accounts` - Create new account
- `PUT /api/finance/accounts/{account}/metadata` - Update account metadata
- `POST /api/finance/accounts/{account}/balance` - Update account balance
- `GET /api/finance/transactions` - List transactions
- `POST /api/finance/transactions` - Add transaction
- `PUT /api/finance/transactions/{id}` - Update transaction
- `DELETE /api/finance/transactions/{id}` - Delete transaction
- `GET /api/finance/summary` - Get financial summary
- `GET /api/finance/categories` - Get finance categories

### Settings & Theme
- `GET /api/settings/theme` - Get current theme
- `POST /api/settings/theme` - Set theme
- `GET /api/settings` - Get all settings
- `POST /api/settings` - Set setting

### General Tracking
- `GET /track/{noun}` - Get all data for a noun
- `POST /track/{noun}` - Add data for a noun
- `GET /track/{noun}/{attribute}` - Get specific attribute data
- `POST /track/{noun}/{attribute}` - Add attribute data

## 🖥️ CLI Commands

The application includes a command-line interface for data management:

```bash
# Set up finance categories
python cli.py setup-categories

# Set up example finance data
python cli.py setup-example-data

# Clear all finance data
python cli.py clear-finance-data

# Clear all data (with confirmation)
python clear_finance_data.py
```

## 🎨 Theme System

The application supports both light and dark themes:

- **Automatic Detection**: Respects system theme preferences
- **Manual Toggle**: Switch themes via settings page
- **Persistent Storage**: Theme preference saved in database
- **Bootstrap 5 Integration**: Uses Bootstrap's native theming system

## 🔒 Security Features

- **Environment Variables**: All sensitive configuration in `.env` files
- **Git Ignore**: Sensitive files excluded from version control
- **No Hardcoded Secrets**: All credentials loaded from environment
- **Database Security**: PostgreSQL with proper access controls

## 📊 Financial Features

### Account Management
- **Hierarchical Grouping**: Accounts grouped by type (Cash, Credit, Loans)
- **Metadata Support**: Institution, account type, and custom notes
- **Balance Tracking**: Automatic and manual balance updates
- **Clickable Rows**: Account rows link to detailed views

### Transaction Tracking
- **Categorization**: Comprehensive category system
- **Required Spending**: Flag transactions as required vs discretionary
- **Metadata Support**: Rich transaction notes with JSON metadata
- **Edit Capabilities**: Full CRUD operations on transactions
- **Balance Integration**: Transactions automatically affect account balances

### Financial Analysis
- **Net Worth Charts**: Historical net worth visualization
- **Spending Analysis**: Monthly spending trends and category breakdown
- **Recent Transactions**: Top 5 recent transactions display
- **Account Summaries**: Individual account statistics and history

## 🛠️ Development

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Features
1. Update models in `app/models.py`
2. Create migration: `alembic revision --autogenerate -m "Feature"`
3. Update CRUD operations in `app/crud.py`
4. Add API endpoints in `app/routers/`
5. Create frontend templates in `app/static/templates/`
6. Update JavaScript in `app/static/js/app.js`

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the security guidelines in `SECURITY.md`
- Open an issue on GitHub 