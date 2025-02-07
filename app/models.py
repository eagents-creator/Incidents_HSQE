from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='incident_only')  # Changed default role
    language = db.Column(db.String(2), default='en')
    can_add_incidents = db.Column(db.Boolean, default=True)
    can_view_incidents = db.Column(db.Boolean, default=False)
    can_add_metrics = db.Column(db.Boolean, default=False)
    can_view_metrics = db.Column(db.Boolean, default=False)
    can_export = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        print(f"Setting password hash for {self.username}: {self.password_hash}")

    def check_password(self, password):
        print(f"Checking password hash: {self.password_hash}")
        result = check_password_hash(self.password_hash, password)
        print(f"Password check result: {result}")
        return result

    def set_role(self, role):
        self.role = role
        # Set permissions based on role
        if role == 'admin':
            self.can_add_incidents = True
            self.can_view_incidents = True
            self.can_add_metrics = True
            self.can_view_metrics = True
            self.can_export = True
            self.is_admin = True
        elif role == 'incident_view':
            self.can_add_incidents = True
            self.can_view_incidents = True
            self.can_add_metrics = False
            self.can_view_metrics = False
            self.can_export = False
            self.is_admin = False
        elif role == 'metrics':
            self.can_add_incidents = False
            self.can_view_incidents = False
            self.can_add_metrics = True
            self.can_view_metrics = True
            self.can_export = True
            self.is_admin = False
        else:  # incident_only
            self.can_add_incidents = True
            self.can_view_incidents = False
            self.can_add_metrics = False
            self.can_view_metrics = False
            self.can_export = False
            self.is_admin = False

    def set_custom_permissions(self, permissions):
        """Set custom permissions for the user"""
        self.can_add_incidents = permissions.get('can_add_incidents', False)
        self.can_view_incidents = permissions.get('can_view_incidents', False)
        self.can_add_metrics = permissions.get('can_add_metrics', False)
        self.can_view_metrics = permissions.get('can_view_metrics', False)
        self.can_export = permissions.get('can_export', False)
        self.is_admin = permissions.get('is_admin', False)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    description = db.Column(db.Text)
    severity = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Open')
    location = db.Column(db.String(100))
    immediate_actions = db.Column(db.Text)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reporter = db.relationship('User', backref='reported_incidents')
    actions = db.relationship('Action', backref='incident', lazy=True)

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Open')
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Creation date
    due_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignee = db.relationship('User', backref='assigned_actions')

class HSQEMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))
    metric_type = db.Column(db.String(100))
    value = db.Column(db.Float)
    unit = db.Column(db.String(50))
    target = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', backref='created_metrics')
