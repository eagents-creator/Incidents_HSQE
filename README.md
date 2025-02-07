# HSQE System

A Health, Safety, Quality, and Environment (HSQE) management system built with Flask.

## Features

- Incident Management
- HSQE Metrics Tracking
- User Management
- Role-based Access Control

## Local Development Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

4. Create admin user:
```bash
python create_admin.py
```
This will create an admin user with:
- Username: admin
- Password: admin

5. Add demo data (optional):
```bash
python add_demo_data.py
```

6. Run the development server:
```bash
python run.py
```
The application will be available at `http://localhost:8082`

## Deployment to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
   - Environment Variables:
     ```
     FLASK_ENV=production
     SECRET_KEY=your-secret-key-here
     DATABASE_URL=your-postgres-url  # Render will provide this automatically
     ```

### Important Notes for Production

1. Change the default SECRET_KEY in production
2. The application will automatically use PostgreSQL in production
3. Database migrations will be run automatically
4. CORS and security settings are automatically configured for production

## Project Structure

```
hsqe_system2/
├── app/                    # Application package
│   ├── static/            # Static files (CSS, JS)
│   ├── templates/         # HTML templates
│   ├── __init__.py        # Application factory
│   ├── auth.py           # Authentication routes
│   ├── main.py           # Main routes
│   └── models.py         # Database models
├── migrations/           # Database migrations
├── wsgi.py              # WSGI entry point
├── run.py               # Development server script
├── requirements.txt     # Python dependencies
├── Procfile            # Render/Heroku deployment config
└── README.md           # This file
```

## Development vs Production

The application uses different configurations based on the environment:

### Development
- SQLite database (hsqe.db in app directory)
- Debug mode enabled
- CSRF protection enabled
- Local development server

### Production
- PostgreSQL database (configured via DATABASE_URL)
- Debug mode disabled
- Secure cookie settings enabled
- HTTPS enforced
- Gunicorn WSGI server
