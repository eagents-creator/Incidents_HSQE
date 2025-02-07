from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, send_file, g
from flask_login import login_required, current_user
from functools import wraps
from .translations import get_text
from app import db
from app.models import Incident, Action, HSQEMetric, User
from datetime import datetime, timedelta
from sqlalchemy import func
import csv
import io
import zipfile

main = Blueprint('main', __name__)

@main.before_request
def before_request():
    g.get_text = lambda key: get_text(key, current_user.language if current_user.is_authenticated else 'en')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash(g.get_text('admin_required'), 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/settings')
@login_required
def settings():
    if current_user.is_admin:
        return render_template('main/settings.html', show_user_management=True)
    return render_template('main/settings.html', show_user_management=False)

@main.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('main/user_management.html', users=users)

@main.route('/user/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if User.query.filter_by(username=username).first():
        flash(g.get_text('username_taken'), 'error')
        return redirect(url_for('main.users'))

    if User.query.filter_by(email=email).first():
        flash(g.get_text('email_taken'), 'error')
        return redirect(url_for('main.users'))

    user = User(username=username, email=email)
    user.set_password(password)
    
    # Set permissions based on form data
    permissions = {
        'can_add_incidents': 'can_add_incidents' in request.form,
        'can_view_incidents': 'can_view_incidents' in request.form,
        'can_add_metrics': 'can_add_metrics' in request.form,
        'can_view_metrics': 'can_view_metrics' in request.form,
        'can_export': 'can_export' in request.form,
        'is_admin': 'is_admin' in request.form
    }
    user.set_custom_permissions(permissions)
    user.role = role

    db.session.add(user)
    db.session.commit()
    flash(g.get_text('user_added'), 'success')
    return redirect(url_for('main.users'))

@main.route('/user/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if User.query.filter(User.username == username, User.id != id).first():
        flash(g.get_text('username_taken'), 'error')
        return redirect(url_for('main.users'))

    if User.query.filter(User.email == email, User.id != id).first():
        flash(g.get_text('email_taken'), 'error')
        return redirect(url_for('main.users'))

    user.username = username
    user.email = email
    if password:
        user.set_password(password)
    
    # Set permissions based on form data
    permissions = {
        'can_add_incidents': 'can_add_incidents' in request.form,
        'can_view_incidents': 'can_view_incidents' in request.form,
        'can_add_metrics': 'can_add_metrics' in request.form,
        'can_view_metrics': 'can_view_metrics' in request.form,
        'can_export': 'can_export' in request.form,
        'is_admin': 'is_admin' in request.form
    }
    user.set_custom_permissions(permissions)
    user.role = role

    db.session.commit()
    flash(g.get_text('user_updated'), 'success')
    return redirect(url_for('main.users'))

@main.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if id == current_user.id:
        flash(g.get_text('cannot_delete_self'), 'error')
        return redirect(url_for('main.users'))
        
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash(g.get_text('user_deleted'), 'success')
    return redirect(url_for('main.users'))

@main.route('/settings/language', methods=['POST'])
@login_required
def update_language():
    language = request.form.get('language')
    if language in ['en', 'fi', 'sv']:
        current_user.language = language
        db.session.commit()
        flash(g.get_text('save'), 'success')
    return redirect(url_for('main.settings'))

@main.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    email = request.form.get('email')
    username = request.form.get('username')
    
    if User.query.filter(User.email == email, User.id != current_user.id).first():
        flash(g.get_text('email_taken'), 'error')
        return redirect(url_for('main.settings'))
    
    if User.query.filter(User.username == username, User.id != current_user.id).first():
        flash(g.get_text('username_taken'), 'error')
        return redirect(url_for('main.settings'))
    
    current_user.email = email
    current_user.username = username
    db.session.commit()
    flash(g.get_text('profile_updated'), 'success')
    return redirect(url_for('main.settings'))

@main.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash(g.get_text('incorrect_password'), 'error')
        return redirect(url_for('main.settings'))
    
    if new_password != confirm_password:
        flash(g.get_text('passwords_dont_match'), 'error')
        return redirect(url_for('main.settings'))
    
    current_user.set_password(new_password)
    db.session.commit()
    flash(g.get_text('password_updated'), 'success')
    return redirect(url_for('main.settings'))

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    # Get date range from request args or default to last month
    now = datetime.now()
    default_from = datetime(now.year, now.month, 1)  # First day of current month
    default_to = now

    try:
        from_date = datetime.strptime(request.args.get('from_date', default_from.strftime('%Y-%m-%d')), '%Y-%m-%d')
        to_date = datetime.strptime(request.args.get('to_date', default_to.strftime('%Y-%m-%d')), '%Y-%m-%d') + timedelta(days=1)
    except (ValueError, TypeError):
        from_date = default_from
        to_date = default_to + timedelta(days=1)

    # Get summary statistics within date range
    total_incidents = Incident.query.filter(Incident.date >= from_date, Incident.date < to_date).count()
    open_actions = Action.query.filter_by(status='Open').filter(Action.due_date >= from_date, Action.due_date < to_date).count()
    recent_incidents = Incident.query.filter(Incident.date >= from_date, Incident.date < to_date).order_by(Incident.date.desc()).limit(20).all()
    
    # Get metrics for charts within date range
    incidents_by_category = db.session.query(
        Incident.category, func.count(Incident.id)
    ).filter(Incident.date >= from_date, Incident.date < to_date).group_by(Incident.category).all()
    
    metrics = HSQEMetric.query.filter(
        HSQEMetric.date >= from_date,
        HSQEMetric.date < to_date
    ).order_by(HSQEMetric.date.desc()).all()
    
    # Format dates for JavaScript
    formatted_metrics = [{
        'date': metric.date.strftime('%Y-%m-%d'),
        'value': metric.value,
        'category': metric.category
    } for metric in metrics]
    
    # Prepare chart data
    categories = ['Health', 'Safety', 'Quality', 'Environment']
    chart_data = {
        'categories': categories,
        'counts': [
            sum(1 for m in formatted_metrics if m['category'] == cat)
            for cat in categories
        ],
        'dates': [m['date'] for m in formatted_metrics],
        'values': [m['value'] for m in formatted_metrics]
    }
    
    # Format incidents by category for chart
    incident_chart_data = {
        'categories': [cat for cat, _ in incidents_by_category],
        'counts': [count for _, count in incidents_by_category]
    }
    
    return render_template('main/dashboard.html',
                         now=now,
                         total_incidents=total_incidents,
                         open_actions=open_actions,
                         recent_incidents=recent_incidents,
                         metrics=formatted_metrics,
                         chart_data=chart_data,
                         incident_chart_data=incident_chart_data)

def permission_required(*permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for permission in permissions:
                if not getattr(current_user, permission, False):
                    flash(g.get_text('permission_denied'), 'error')
                    return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@main.route('/incidents', methods=['GET', 'POST'])
@login_required
@permission_required('can_add_incidents')
def incidents():
    if request.method == 'POST':
        incident = Incident(
            category=request.form.get('category'),
            subcategory=request.form.get('subcategory'),
            description=request.form.get('description'),
            severity=request.form.get('severity'),
            location=request.form.get('location'),
            immediate_actions=request.form.get('immediate_actions'),
            reporter=current_user
        )
        db.session.add(incident)
        db.session.commit()
        flash('Incident reported successfully', 'success')
        return redirect(url_for('main.incidents'))
    
    # Get date range from request args or default to last month
    now = datetime.now()
    default_from = datetime(now.year, now.month, 1)  # First day of current month
    default_to = now

    try:
        from_date = datetime.strptime(request.args.get('from_date', default_from.strftime('%Y-%m-%d')), '%Y-%m-%d')
        to_date = datetime.strptime(request.args.get('to_date', default_to.strftime('%Y-%m-%d')), '%Y-%m-%d') + timedelta(days=1)
    except (ValueError, TypeError):
        from_date = default_from
        to_date = default_to + timedelta(days=1)

    incidents = Incident.query.filter(
        Incident.date >= from_date,
        Incident.date < to_date
    ).order_by(Incident.date.desc()).limit(20).all()

    return render_template('main/incidents.html', 
                         incidents=incidents,
                         now=now,
                         from_date=from_date,
                         to_date=to_date)

@main.route('/actions', methods=['GET', 'POST'])
@login_required
def actions():
    if request.method == 'POST':
        action = Action(
            title=request.form.get('title'),
            description=request.form.get('description'),
            type=request.form.get('type'),
            priority=request.form.get('priority'),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d'),
            incident_id=request.form.get('incident_id'),
            assignee_id=request.form.get('assignee_id')
        )
        db.session.add(action)
        db.session.commit()
        flash('Action created successfully', 'success')
        return redirect(url_for('main.actions'))
    
    # Get date range from request args or default to last month
    now = datetime.now()
    default_from = datetime(now.year, now.month, 1)  # First day of current month
    default_to = now

    try:
        from_date = datetime.strptime(request.args.get('from_date', default_from.strftime('%Y-%m-%d')), '%Y-%m-%d')
        to_date = datetime.strptime(request.args.get('to_date', default_to.strftime('%Y-%m-%d')), '%Y-%m-%d') + timedelta(days=1)
    except (ValueError, TypeError):
        from_date = default_from
        to_date = default_to + timedelta(days=1)

    actions = Action.query.filter(
        Action.due_date >= from_date,
        Action.due_date < to_date
    ).order_by(Action.due_date.asc()).limit(20).all()
    
    incidents = Incident.query.all()
    users = User.query.all()
    
    return render_template('main/actions.html', 
                         actions=actions,
                         incidents=incidents,
                         users=users,
                         now=now,
                         from_date=from_date,
                         to_date=to_date)

@main.route('/metrics', methods=['GET', 'POST'])
@login_required
@permission_required('can_add_metrics', 'can_view_metrics')
def metrics():
    if request.method == 'POST':
        metric_type = request.form.get('metric_type')
        value = float(request.form.get('value'))
        
        # Calculate target based on metric type
        target = request.form.get('target')
        if not target:  # Only set automatic target if none provided
            if 'Rate' in metric_type or 'Incidents' in metric_type or 'Defect' in metric_type:
                target = 0  # Target should be zero for incidents, defects, etc.
            elif 'Compliance' in metric_type or 'Coverage' in metric_type or 'Completion' in metric_type:
                target = 100  # Target should be 100% for compliance
            elif 'Score' in metric_type or 'Satisfaction' in metric_type:
                unit = request.form.get('unit')
                if 'out of 100' in unit:
                    target = 100
                elif 'out of 10' in unit:
                    target = 10
            elif 'Consumption' in metric_type or 'Usage' in metric_type or 'Emissions' in metric_type:
                target = 0  # Target should be minimum for consumption
            elif 'Yield' in metric_type or 'Recycling' in metric_type:
                target = 100  # Target should be maximum for yield/recycling
        
        metric = HSQEMetric(
            category=request.form.get('category'),
            metric_type=metric_type,
            value=value,
            unit=request.form.get('unit'),
            target=float(target) if target else None,
            notes=request.form.get('notes'),
            created_by_id=current_user.id
        )
        db.session.add(metric)
        db.session.commit()
        flash(g.get_text('metric_added'), 'success')
        return redirect(url_for('main.metrics'))
    
    # Get date range from request args or default to last month
    now = datetime.now()
    default_from = datetime(now.year, now.month, 1)  # First day of current month
    default_to = now

    try:
        from_date = datetime.strptime(request.args.get('from_date', default_from.strftime('%Y-%m-%d')), '%Y-%m-%d')
        to_date = datetime.strptime(request.args.get('to_date', default_to.strftime('%Y-%m-%d')), '%Y-%m-%d') + timedelta(days=1)
    except (ValueError, TypeError):
        from_date = default_from
        to_date = default_to + timedelta(days=1)

    metrics = HSQEMetric.query.join(User).filter(
        HSQEMetric.date >= from_date,
        HSQEMetric.date < to_date
    ).order_by(HSQEMetric.date.desc()).all()
    
    # Format metrics data for charts
    formatted_metrics = [{
        'id': metric.id,
        'date': metric.date.strftime('%Y-%m-%d'),
        'category': metric.category,
        'metric_type': metric.metric_type,
        'value': float(metric.value),
        'unit': metric.unit,
        'target': float(metric.target) if metric.target else None,
        'notes': metric.notes,
        'created_by': metric.created_by.username if metric.created_by else 'Unknown'
    } for metric in metrics]

    # Prepare chart data
    categories = ['Health', 'Safety', 'Quality', 'Environment']
    
    # Calculate metrics by category
    metrics_by_category = {}
    for cat in categories:
        cat_metrics = [m for m in formatted_metrics if m['category'] == cat]
        metrics_by_category[cat] = len(cat_metrics)

    # Calculate metrics trend (average value per day)
    metrics_by_date = {}
    for metric in formatted_metrics:
        date = metric['date']
        if date not in metrics_by_date:
            metrics_by_date[date] = []
        metrics_by_date[date].append(metric['value'])

    trend_dates = sorted(metrics_by_date.keys())
    trend_values = [sum(metrics_by_date[date])/len(metrics_by_date[date]) 
                   for date in trend_dates]

    chart_data = {
        'categories': categories,
        'counts': [metrics_by_category[cat] for cat in categories],
        'dates': trend_dates,
        'values': trend_values
    }

    # Ensure chart_data has default values if empty
    if not formatted_metrics:
        chart_data = {
            'categories': categories,
            'counts': [0, 0, 0, 0],
            'dates': [],
            'values': []
        }
    
    return render_template('main/metrics.html', 
                         metrics=formatted_metrics,
                         chart_data=chart_data,
                         from_date=from_date,
                         to_date=to_date)

@main.route('/metric/<int:id>/edit', methods=['POST'])
@login_required
@permission_required('can_add_metrics')
def edit_metric(id):
    metric = HSQEMetric.query.get_or_404(id)
    if request.method == 'POST':
        metric.category = request.form.get('category')
        metric.metric_type = request.form.get('metric_type')
        metric.value = float(request.form.get('value'))
        metric.unit = request.form.get('unit')
        metric.target = float(request.form.get('target')) if request.form.get('target') else None
        metric.notes = request.form.get('notes')
        db.session.commit()
        flash('Metric updated successfully', 'success')
    return redirect(url_for('main.metrics'))

@main.route('/metric/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('can_add_metrics')
def delete_metric(id):
    metric = HSQEMetric.query.get_or_404(id)
    db.session.delete(metric)
    db.session.commit()
    flash('Metric deleted successfully', 'success')
    return redirect(url_for('main.metrics'))

@main.route('/action/<int:id>/update', methods=['POST'])
@login_required
@permission_required('can_add_incidents')
def update_action(id):
    action = Action.query.get_or_404(id)
    if request.method == 'POST':
        # Update fields only if they are provided in the form
        if request.form.get('title'):
            action.title = request.form.get('title')
        if request.form.get('description'):
            action.description = request.form.get('description')
        if request.form.get('type'):
            action.type = request.form.get('type')
        if request.form.get('priority'):
            action.priority = request.form.get('priority')
        if request.form.get('status'):
            action.status = request.form.get('status')
        if request.form.get('due_date'):
            action.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
        
        # Set completion date when status changes to Completed
        if action.status == 'Completed' and not action.completion_date:
            action.completion_date = datetime.utcnow()
        db.session.commit()
        flash('Action updated successfully', 'success')
    return redirect(url_for('main.actions'))

@main.route('/action/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('can_add_incidents')
def delete_action(id):
    action = Action.query.get_or_404(id)
    db.session.delete(action)
    db.session.commit()
    flash('Action deleted successfully', 'success')
    return redirect(url_for('main.actions'))

@main.route('/incident/<int:id>/update', methods=['POST'])
@login_required
@permission_required('can_add_incidents')
def update_incident(id):
    incident = Incident.query.get_or_404(id)
    incident.status = request.form.get('status')
    db.session.commit()
    flash(g.get_text('incident_updated'), 'success')
    return redirect(request.referrer or url_for('main.incidents'))

@main.route('/incident/<int:id>/edit', methods=['POST'])
@login_required
@permission_required('can_add_incidents')
def edit_incident(id):
    incident = Incident.query.get_or_404(id)
    incident.category = request.form.get('category')
    incident.subcategory = request.form.get('subcategory')
    incident.description = request.form.get('description')
    incident.severity = request.form.get('severity')
    incident.location = request.form.get('location')
    incident.immediate_actions = request.form.get('immediate_actions')
    db.session.commit()
    flash('Incident updated successfully', 'success')
    return redirect(url_for('main.incidents'))

@main.route('/incident/<int:id>/delete', methods=['POST'])
@login_required
@permission_required('can_add_incidents')
def delete_incident(id):
    incident = Incident.query.get_or_404(id)
    db.session.delete(incident)
    db.session.commit()
    flash('Incident deleted successfully', 'success')
    return redirect(url_for('main.incidents'))

@main.route('/incidents/export', methods=['POST'])
@login_required
@permission_required('can_export')
def export_incidents():
    from_date = datetime.strptime(request.form.get('from_date'), '%Y-%m-%d')
    to_date = datetime.strptime(request.form.get('to_date'), '%Y-%m-%d')
    
    incidents = Incident.query.filter(
        Incident.date >= from_date,
        Incident.date <= to_date + timedelta(days=1)  # Include the entire end day
    ).order_by(Incident.date.desc()).all()
    
    # Create CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Category', 'Subcategory', 'Description', 'Severity', 
                    'Status', 'Location', 'Immediate Actions', 'Reporter'])
    
    for incident in incidents:
        writer.writerow([
            incident.date.strftime('%Y-%m-%d %H:%M'),
            incident.category,
            incident.subcategory,
            incident.description,
            incident.severity,
            incident.status,
            incident.location,
            incident.immediate_actions,
            incident.reporter.username if incident.reporter else 'Unknown'
        ])
    
    # Create the response
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=incidents_{from_date.strftime("%Y%m%d")}_to_{to_date.strftime("%Y%m%d")}.csv'
        }
    )

@main.route('/dashboard/export', methods=['POST'])
@login_required
@permission_required('can_export')
def export_dashboard():
    from_date = datetime.strptime(request.form.get('from_date'), '%Y-%m-%d')
    to_date = datetime.strptime(request.form.get('to_date'), '%Y-%m-%d') + timedelta(days=1)
    
    # Create a ZIP file containing the requested exports
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        # Export incidents if requested
        if 'export_incidents' in request.form:
            incidents = Incident.query.filter(
                Incident.date >= from_date,
                Incident.date < to_date
            ).order_by(Incident.date.desc()).all()
            
            incidents_output = io.StringIO()
            writer = csv.writer(incidents_output)
            writer.writerow(['Date', 'Category', 'Subcategory', 'Description', 'Severity', 
                           'Status', 'Location', 'Immediate Actions', 'Reporter'])
            
            for incident in incidents:
                writer.writerow([
                    incident.date.strftime('%Y-%m-%d %H:%M'),
                    incident.category,
                    incident.subcategory,
                    incident.description,
                    incident.severity,
                    incident.status,
                    incident.location,
                    incident.immediate_actions,
                    incident.reporter.username if incident.reporter else 'Unknown'
                ])
            
            zf.writestr('incidents.csv', incidents_output.getvalue())
        
        # Export actions if requested
        if 'export_actions' in request.form:
            actions = Action.query.filter(
                Action.due_date >= from_date,
                Action.due_date < to_date
            ).order_by(Action.due_date.desc()).all()
            
            actions_output = io.StringIO()
            writer = csv.writer(actions_output)
            writer.writerow(['Title', 'Description', 'Type', 'Priority', 'Status',
                           'Due Date', 'Completion Date', 'Assignee', 'Related Incident'])
            
            for action in actions:
                writer.writerow([
                    action.title,
                    action.description,
                    action.type,
                    action.priority,
                    action.status,
                    action.due_date.strftime('%Y-%m-%d'),
                    action.completion_date.strftime('%Y-%m-%d') if action.completion_date else '',
                    action.assignee.username if action.assignee else 'Unknown',
                    f"{action.incident.category} - {action.incident.subcategory}" if action.incident else 'N/A'
                ])
            
            zf.writestr('actions.csv', actions_output.getvalue())
        
        # Export metrics if requested
        if 'export_metrics' in request.form:
            metrics = HSQEMetric.query.filter(
                HSQEMetric.date >= from_date,
                HSQEMetric.date < to_date
            ).order_by(HSQEMetric.date.desc()).all()
            
            metrics_output = io.StringIO()
            writer = csv.writer(metrics_output)
            writer.writerow(['Date', 'Category', 'Metric Type', 'Value', 'Unit',
                           'Target', 'Notes', 'Created By'])
            
            for metric in metrics:
                writer.writerow([
                    metric.date.strftime('%Y-%m-%d'),
                    metric.category,
                    metric.metric_type,
                    metric.value,
                    metric.unit,
                    metric.target,
                    metric.notes,
                    metric.created_by.username if metric.created_by else 'Unknown'
                ])
            
            zf.writestr('metrics.csv', metrics_output.getvalue())
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'hsqe_data_{from_date.strftime("%Y%m%d")}_to_{to_date.strftime("%Y%m%d")}.zip'
    )

@main.route('/reports')
@login_required
@permission_required('can_view_metrics', 'can_view_incidents')
def reports():
    # Get incidents by month
    incidents_by_month = db.session.query(
        func.strftime('%Y-%m', Incident.date).label('month'),
        func.count(Incident.id)
    ).group_by('month').order_by('month').all()
    
    # Get actions by status
    actions_by_status = db.session.query(
        Action.status, func.count(Action.id)
    ).group_by(Action.status).all()
    
    # Get metrics
    metrics = HSQEMetric.query.order_by(HSQEMetric.date.desc()).limit(50).all()
    
    # Get incidents by category
    incidents_by_category = db.session.query(
        Incident.category, func.count(Incident.id)
    ).group_by(Incident.category).all()
    
    # Get actions by category and status
    open_actions_by_category = db.session.query(
        Incident.category, func.count(Action.id)
    ).join(Action).filter(Action.status == 'Open').group_by(Incident.category).all()
    
    completed_actions_by_category = db.session.query(
        Incident.category, func.count(Action.id)
    ).join(Action).filter(Action.status == 'Completed').group_by(Incident.category).all()
    
    # Calculate average response times
    response_times = db.session.query(
        Incident.category,
        func.avg(func.julianday(Action.completion_date) - func.julianday(Incident.date))
    ).join(Action).filter(Action.completion_date != None).group_by(Incident.category).all()
    
    # Calculate target compliance
    target_compliance = {}
    for category in ['Health', 'Safety', 'Quality', 'Environment']:
        category_metrics = [m for m in metrics if m.category == category and m.target is not None]
        if category_metrics:
            compliant = sum(1 for m in category_metrics if m.value <= m.target)
            target_compliance[category] = (compliant / len(category_metrics)) * 100
        else:
            target_compliance[category] = 0
    
    # Format data for charts
    chart_data = {
        'incidents': {
            'months': [month for month, _ in incidents_by_month],
            'counts': [count for _, count in incidents_by_month]
        },
        'actions': {
            'statuses': [status for status, _ in actions_by_status],
            'counts': [count for _, count in actions_by_status]
        },
        'metrics': {
            'dates': [metric.date.strftime('%Y-%m-%d') for metric in metrics],
            'values': [float(metric.value) for metric in metrics],
            'targets': [float(metric.target) if metric.target else None for metric in metrics]
        }
    }
    
    # Convert query results to dictionaries for easier template access
    incidents_by_category_dict = dict(incidents_by_category)
    open_actions_by_category_dict = dict(open_actions_by_category)
    completed_actions_by_category_dict = dict(completed_actions_by_category)
    response_times_dict = dict(response_times)
    
    return render_template('main/reports.html',
                         chart_data=chart_data,
                         incidents_by_category=incidents_by_category_dict,
                         open_actions_by_category=open_actions_by_category_dict,
                         completed_actions_by_category=completed_actions_by_category_dict,
                         response_times=response_times_dict,
                         target_compliance=target_compliance)
