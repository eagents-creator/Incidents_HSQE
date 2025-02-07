from flask import Blueprint, request, jsonify
from flask_login import login_required
from app import db
from app.models import Incident, Action, HSQEMetric, User
from datetime import datetime
from functools import wraps

api_bp = Blueprint('api', __name__)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'No API key provided'}), 401
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Incidents API
@api_bp.route('/incidents', methods=['GET'])
@require_api_key
def get_incidents():
    incidents = Incident.query.all()
    return jsonify([{
        'id': i.id,
        'category': i.category,
        'subcategory': i.subcategory,
        'description': i.description,
        'date': i.date.isoformat(),
        'severity': i.severity,
        'status': i.status,
        'location': i.location,
        'reporter_id': i.reporter_id
    } for i in incidents])

@api_bp.route('/incidents', methods=['POST'])
@require_api_key
def create_incident():
    data = request.get_json()
    
    required_fields = ['category', 'subcategory', 'description', 'severity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    incident = Incident(
        category=data['category'],
        subcategory=data['subcategory'],
        description=data['description'],
        severity=data['severity'],
        location=data.get('location'),
        immediate_actions=data.get('immediate_actions'),
        reporter_id=data.get('reporter_id')
    )
    
    db.session.add(incident)
    db.session.commit()
    
    return jsonify({
        'message': 'Incident created successfully',
        'id': incident.id
    }), 201

# Actions API
@api_bp.route('/actions', methods=['GET'])
@require_api_key
def get_actions():
    actions = Action.query.all()
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'description': a.description,
        'type': a.type,
        'priority': a.priority,
        'status': a.status,
        'due_date': a.due_date.isoformat() if a.due_date else None,
        'completion_date': a.completion_date.isoformat() if a.completion_date else None,
        'incident_id': a.incident_id,
        'assignee_id': a.assignee_id
    } for a in actions])

@api_bp.route('/actions', methods=['POST'])
@require_api_key
def create_action():
    data = request.get_json()
    
    required_fields = ['title', 'type', 'priority']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    action = Action(
        title=data['title'],
        description=data.get('description'),
        type=data['type'],
        priority=data['priority'],
        due_date=datetime.fromisoformat(data['due_date']) if 'due_date' in data else None,
        incident_id=data.get('incident_id'),
        assignee_id=data.get('assignee_id')
    )
    
    db.session.add(action)
    db.session.commit()
    
    return jsonify({
        'message': 'Action created successfully',
        'id': action.id
    }), 201

# Metrics API
@api_bp.route('/metrics', methods=['GET'])
@require_api_key
def get_metrics():
    metrics = HSQEMetric.query.all()
    return jsonify([{
        'id': m.id,
        'category': m.category,
        'metric_type': m.metric_type,
        'value': m.value,
        'unit': m.unit,
        'date': m.date.isoformat(),
        'target': m.target,
        'notes': m.notes
    } for m in metrics])

@api_bp.route('/metrics', methods=['POST'])
@require_api_key
def create_metric():
    data = request.get_json()
    
    required_fields = ['category', 'metric_type', 'value']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    metric = HSQEMetric(
        category=data['category'],
        metric_type=data['metric_type'],
        value=float(data['value']),
        unit=data.get('unit'),
        target=float(data['target']) if 'target' in data else None,
        notes=data.get('notes'),
        created_by_id=data.get('created_by_id')
    )
    
    db.session.add(metric)
    db.session.commit()
    
    return jsonify({
        'message': 'Metric created successfully',
        'id': metric.id
    }), 201

# Statistics API
@api_bp.route('/statistics', methods=['GET'])
@require_api_key
def get_statistics():
    total_incidents = Incident.query.count()
    open_actions = Action.query.filter_by(status='Open').count()
    incidents_by_category = db.session.query(
        Incident.category, db.func.count(Incident.id)
    ).group_by(Incident.category).all()
    
    return jsonify({
        'total_incidents': total_incidents,
        'open_actions': open_actions,
        'incidents_by_category': dict(incidents_by_category)
    })
