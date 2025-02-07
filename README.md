# HSQE System

A Health, Safety, Quality, and Environment (HSQE) management system built with Flask.

## Features

- Incident Management
- HSQE Metrics Tracking
- User Management
- Role-based Access Control

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd hsqe_system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):
```bash
export FLASK_ENV=development
export SECRET_KEY=your-secret-key
```

## Running the Application

1. Initialize the database:
```bash
flask db upgrade
```

2. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:8081`

## Project Structure

```
hsqe_system/
├── app/                    # Application package
│   ├── static/            # Static files (CSS, JS)
│   ├── templates/         # HTML templates
│   ├── __init__.py        # Application factory
│   ├── auth.py           # Authentication routes
│   ├── main.py           # Main routes
│   └── models.py         # Database models
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Development

- The database file (hsqe.db) is stored in the app directory
- Flask debug mode is enabled by default in development
- CORS is enabled for development purposes

## Security Notes

- Change the default SECRET_KEY in production
- Enable secure cookie settings in production
- Review CORS settings before deployment
