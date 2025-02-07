from app import create_app, db
from app.models import User, Incident, Action, HSQEMetric
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

def add_demo_data():
    print("Starting demo data creation...")
    try:
        app = create_app()
        print("App created successfully")
        with app.app_context():
            print("Entered app context")
            print("Creating database tables in add_demo_data...")
            db.create_all()
            print("Database tables created in add_demo_data")
            
            # Verify database connection
            try:
                db.session.execute('SELECT 1')
                print("Database connection verified")
            except Exception as e:
                print(f"Database connection error: {str(e)}")
                raise e
            # Clear existing data
            HSQEMetric.query.delete()
            Action.query.delete()
            Incident.query.delete()
            User.query.delete()
            db.session.commit()

            print("Creating admin user...")
            try:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    role='admin'
                )
                admin.set_password('admin')
                admin.set_role('admin')  # This will set all admin permissions
                db.session.add(admin)
                db.session.commit()  # Commit immediately to ensure admin is created
                print("Admin user created successfully")
                
                # Verify admin user was created
                admin_check = User.query.filter_by(username='admin').first()
                if admin_check:
                    print(f"Admin user verified in database with id: {admin_check.id}")
                else:
                    print("ERROR: Admin user not found in database after creation")
            except Exception as e:
                print(f"Error creating admin user: {str(e)}")
                db.session.rollback()
                raise e

            # Create users with different roles
            users = [admin]
            
            # Incident-only user
            incident_user = User(username='incident_user', email='incident@example.com', role='incident_only')
            incident_user.set_password('password')
            incident_user.set_role('incident_only')
            users.append(incident_user)
            db.session.add(incident_user)
            
            # Incident-view user
            incident_view_user = User(username='incident_view', email='incident_view@example.com', role='incident_view')
            incident_view_user.set_password('password')
            incident_view_user.set_role('incident_view')
            users.append(incident_view_user)
            db.session.add(incident_view_user)
            
            # Metrics user
            metrics_user = User(username='metrics_user', email='metrics@example.com', role='metrics')
            metrics_user.set_password('password')
            metrics_user.set_role('metrics')
            users.append(metrics_user)
            db.session.add(metrics_user)
            db.session.commit()

            print("Creating incidents...")
            incidents = []
            now = datetime.now()
            for _ in range(50):
                scenario = random.choice(incident_scenarios)
                subcategory_info = random.choice(scenario['subcategories'])
                
                date = now - timedelta(days=random.randint(0, 180))
                incident = Incident(
                    category=scenario['category'],
                    subcategory=subcategory_info[0],
                    description=subcategory_info[1],
                    date=date,
                    severity=subcategory_info[2],
                    status=random.choice(['Open', 'Closed']),
                    location=random.choice(['Building A', 'Building B', 'Workshop', 'Laboratory', 'Office']),
                    immediate_actions='Immediate containment actions taken and area secured',
                    reporter=random.choice(users)
                )
                incidents.append(incident)
                db.session.add(incident)
            db.session.commit()

            print("Creating actions...")
            action_types = ['Corrective', 'Preventive']
            action_priorities = ['High', 'Medium', 'Low']
            action_statuses = ['Open', 'In Progress', 'Completed']

            for incident in incidents:
                num_actions = random.randint(1, 3)
                for _ in range(num_actions):
                    due_date = incident.date + timedelta(days=random.randint(7, 30))
                    status = random.choice(action_statuses)
                    completion_date = None
                    if status == 'Completed':
                        completion_date = due_date - timedelta(days=random.randint(0, 7))

                    action = Action(
                        title=f'Action for {incident.category} - {incident.subcategory}',
                        description=f'Implement measures to prevent recurrence of {incident.description.lower()}',
                        type=random.choice(action_types),
                        priority=random.choice(action_priorities),
                        status=status,
                        due_date=due_date,
                        completion_date=completion_date,
                        incident=incident,
                        assignee=random.choice(users)
                    )
                    db.session.add(action)
            db.session.commit()

            print("Creating metrics...")
            metric_types = {
                'Health': [
                    ('Lost Time Injury Rate', 'Incidents per million hours worked', 0, 5, 1),
                    ('Sick Leave Rate', 'Percentage', 0, 10, 3),
                    ('Health Check Compliance', 'Percentage', 50, 100, 100),
                    ('Ergonomic Assessment Score', 'Score out of 100', 60, 100, 90),
                    ('Workplace Satisfaction', 'Score out of 10', 5, 10, 8.5)
                ],
                'Safety': [
                    ('Near Miss Reports', 'Count per month', 0, 20, 15),
                    ('Safety Training Completion', 'Percentage', 70, 100, 100),
                    ('PPE Compliance Rate', 'Percentage', 80, 100, 100),
                    ('Risk Assessment Coverage', 'Percentage', 60, 100, 100),
                    ('Emergency Response Time', 'Minutes', 1, 10, 3)
                ],
                'Quality': [
                    ('First Pass Yield', 'Percentage', 85, 100, 98),
                    ('Customer Satisfaction', 'Score out of 10', 7, 10, 9.5),
                    ('Defect Rate', 'Parts per million', 0, 1000, 100),
                    ('On-Time Delivery', 'Percentage', 80, 100, 98),
                    ('Process Capability Index', 'Cp value', 1, 2, 1.67)
                ],
                'Environment': [
                    ('Energy Consumption', 'kWh per unit', 50, 200, 100),
                    ('Water Usage', 'Cubic meters per day', 10, 50, 20),
                    ('Waste Recycling Rate', 'Percentage', 40, 100, 90),
                    ('Carbon Emissions', 'Tons CO2e per month', 10, 100, 30),
                    ('Environmental Incidents', 'Count per month', 0, 5, 0)
                ]
            }

            current_date = now - timedelta(days=180)
            while current_date <= now:
                for category, metrics in metric_types.items():
                    for metric_type, unit, min_val, max_val, target in metrics:
                        value = random.uniform(min_val, max_val)
                        
                        # Define target based on metric type
                        if 'Rate' in metric_type or 'Incidents' in metric_type or 'Defect' in metric_type:
                            target = 0  # Target should be zero for incidents, defects, etc.
                        elif 'Compliance' in metric_type or 'Coverage' in metric_type or 'Completion' in metric_type:
                            target = 100  # Target should be 100% for compliance
                        elif 'Score' in metric_type or 'Satisfaction' in metric_type:
                            target = max_val  # Target should be maximum possible score
                        elif 'Consumption' in metric_type or 'Usage' in metric_type or 'Emissions' in metric_type:
                            target = min_val  # Target should be minimum for consumption
                        else:
                            target = max_val if 'Yield' in metric_type or 'Recycling' in metric_type else min_val
                        
                        metric = HSQEMetric(
                            category=category,
                            metric_type=metric_type,
                            value=round(value, 2),
                            unit=unit,
                            date=current_date,
                            target=target,
                            notes=f'Regular measurement of {metric_type.lower()}',
                            created_by=random.choice(users)
                        )
                        db.session.add(metric)
                current_date += timedelta(days=1)
            db.session.commit()

            print("Demo data added successfully!")
            print("Exiting app context")
    except Exception as e:
        print(f"Error in add_demo_data: {str(e)}")
        raise e

# Incident scenarios
incident_scenarios = [
    {
        'category': 'Health',
        'subcategories': [
            ('Illness', 'Employee reported flu-like symptoms', 'Low'),
            ('Injury', 'Minor cut while handling equipment', 'Low'),
            ('Ergonomic Issue', 'Reported wrist pain from computer use', 'Medium'),
            ('Mental Health', 'Stress due to high workload', 'Medium'),
            ('Occupational Health', 'Exposure to loud noise', 'High')
        ]
    },
    {
        'category': 'Safety',
        'subcategories': [
            ('Near Miss', 'Almost slipped on wet floor', 'Low'),
            ('Property Damage', 'Equipment damaged during operation', 'Medium'),
            ('Fire Safety', 'Smoke detector malfunction', 'High'),
            ('Electrical Safety', 'Exposed wiring found', 'High'),
            ('Chemical Safety', 'Chemical spill in laboratory', 'High')
        ]
    },
    {
        'category': 'Quality',
        'subcategories': [
            ('Product Defect', 'Product packaging issue', 'Medium'),
            ('Process Deviation', 'Production process parameter out of range', 'Medium'),
            ('Documentation Error', 'Incorrect version of procedure used', 'Low'),
            ('Equipment Malfunction', 'Calibration error in testing equipment', 'High'),
            ('Customer Complaint', 'Product quality below specification', 'High')
        ]
    },
    {
        'category': 'Environment',
        'subcategories': [
            ('Spill', 'Minor oil spill in workshop', 'Medium'),
            ('Emission', 'Excessive dust emission from ventilation', 'High'),
            ('Waste Management', 'Improper waste segregation', 'Medium'),
            ('Energy Usage', 'Unusually high energy consumption', 'Low'),
            ('Water Usage', 'Water leak in facility', 'Medium')
        ]
    }
]

if __name__ == '__main__':
    add_demo_data()
