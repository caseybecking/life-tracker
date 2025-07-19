# Life Tracker

A comprehensive life tracking application built with Python FastAPI backend and modern frontend to track various aspects of life including finances, personal data, home maintenance, and more.

## Features

- **Financial Tracking**: Track bank accounts, transactions, balances
- **Personal Data**: Track weight, health metrics, personal information
- **Home Management**: Track home maintenance, pool care, BBQ cleaning
- **Activities**: Track sports, games, scores, dates
- **Flexible Schema**: Entity-attribute-value (EAV) model for maximum flexibility

## Database Structure

The application uses an Entity-Attribute-Value (EAV) model:

- **Nouns**: Main categories (Banking, Person, Home, Vehicle, Hockey)
- **Attributes**: Properties of nouns (Transaction, Casey, Garden, 4-Runner)
- **Values**: Specific data points (Category, Weight, Mowing, Fuel_Gallons)
- **Data**: Actual values (Income, 165, 10-8-2019, 16.516)

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials
   ```

3. **Set up database**:
   ```bash
   # Create PostgreSQL database
   createdb life_tracker
   
   # Run migrations
   alembic upgrade head
   ```

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the application**:
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:8000/finance
   - API Documentation: http://localhost:8000/docs

## Project Structure

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
│       ├── js/
│       └── templates/
├── alembic/                 # Database migrations
├── requirements.txt
└── README.md
```

## API Endpoints

### Financial Tracking
- `GET /finance/accounts` - List all bank accounts
- `POST /finance/accounts` - Create new account
- `GET /finance/transactions` - List transactions
- `POST /finance/transactions` - Add transaction
- `GET /finance/balance/{account_id}` - Get account balance

### General Tracking
- `GET /track/{noun}` - Get all data for a noun
- `POST /track/{noun}` - Add data for a noun
- `GET /track/{noun}/{attribute}` - Get specific attribute data
- `POST /track/{noun}/{attribute}` - Add attribute data

## Database Schema

The application uses PostgreSQL with the following main tables:

- `nouns` - Main categories (Banking, Person, Home, etc.)
- `attributes` - Properties of nouns
- `values` - Data types for attributes
- `data` - Actual tracked values

This flexible schema allows tracking any type of data without schema changes. 