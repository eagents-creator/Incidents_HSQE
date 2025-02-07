# HSQE Management System

A comprehensive Health, Safety, Quality, and Environment (HSQE) management system built with Flask.

## Features

- **Health, Safety, Quality, and Environment Management**
  - Incident reporting and tracking
  - Action management (corrective & preventive)
  - Metrics tracking and analysis
  - Comprehensive reporting

- **User Management**
  - User authentication and authorization
  - Role-based access control
  - Profile management

- **Dashboard & Analytics**
  - Real-time statistics
  - Interactive charts
  - Performance metrics

- **REST API**
  - External system integration
  - API key authentication
  - Comprehensive documentation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hsqe_system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
flask db upgrade
```

## Configuration

Create a `.env` file in the project root with the following variables:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///hsqe.db
```

## Running the Application

1. Start the development server:
```bash
flask run
```

2. Access the application at `http://localhost:5000`

## Project Structure

```
hsqe_system/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── auth.py
│   ├── main.py
│   ├── api.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│       ├── auth/
│       └── main/
├── migrations/
├── tests/
├── venv/
├── .env
├── config.py
├── requirements.txt
└── run.py
```

## API Documentation

### Authentication

All API endpoints require an API key to be included in the request header:
```
X-API-Key: your-api-key-here
```

### Endpoints

#### Incidents
- `GET /api/incidents` - List all incidents
- `POST /api/incidents` - Create new incident
- `GET /api/incidents/<id>` - Get incident details
- `PUT /api/incidents/<id>` - Update incident
- `DELETE /api/incidents/<id>` - Delete incident

#### Actions
- `GET /api/actions` - List all actions
- `POST /api/actions` - Create new action
- `GET /api/actions/<id>` - Get action details
- `PUT /api/actions/<id>` - Update action
- `DELETE /api/actions/<id>` - Delete action

#### Metrics
- `GET /api/metrics` - List all metrics
- `POST /api/metrics` - Create new metric
- `GET /api/metrics/<id>` - Get metric details
- `PUT /api/metrics/<id>` - Update metric
- `DELETE /api/metrics/<id>` - Delete metric

## Testing

Run the test suite:
```bash
pytest
```

Generate coverage report:
```bash
pytest --cov=app tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
