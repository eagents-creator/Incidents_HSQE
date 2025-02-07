from app import create_app, db
from app.models import User, Incident, Action, HSQEMetric
from datetime import datetime, timedelta
import random

def add_demo_data():
    print("Starting demo data creation...")
    
    app = create_app()
    with app.app_context():
        # Create incidents
        print("Creating incidents...")
        categories = ['Health', 'Safety', 'Quality', 'Environment']
        subcategories = {
            'Health': ['Illness', 'Injury', 'Ergonomic Issue'],
            'Safety': ['Near Miss', 'Property Damage', 'Fire Safety'],
            'Quality': ['Product Defect', 'Process Deviation', 'Documentation Error'],
            'Environment': ['Spill', 'Emission', 'Waste Management']
        }
        severities = ['Low', 'Medium', 'High']
        locations = ['Building A', 'Building B', 'Warehouse', 'Production Line 1', 'Production Line 2']
        
        # Get admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Error: Admin user not found")
            return
        
        for _ in range(20):
            category = random.choice(categories)
            incident = Incident(
                category=category,
                subcategory=random.choice(subcategories[category]),
                description=f"Demo incident description for {category.lower()} issue.",
                severity=random.choice(severities),
                location=random.choice(locations),
                immediate_actions="Immediate actions taken to address the issue.",
                date=datetime.now() - timedelta(days=random.randint(0, 30)),
                status=random.choice(['Open', 'Closed']),
                reporter=admin
            )
            db.session.add(incident)

        # Create actions
        print("Creating actions...")
        action_types = ['Corrective', 'Preventive', 'Investigation']
        priorities = ['Low', 'Medium', 'High']
        
        incidents = Incident.query.all()
        for incident in incidents:
            # Create 3-5 actions per incident
            for _ in range(random.randint(3, 5)):
                action_date = datetime.now() - timedelta(days=random.randint(0, 30))
                due_date = action_date + timedelta(days=random.randint(14, 90))
                status = random.choice(['Open', 'In Progress', 'Completed'])
                
                action_verbs = ['Investigate', 'Review', 'Implement', 'Monitor', 'Train']
                improvement_types = [
                    'Root cause analysis',
                    'Process improvement',
                    'Training program',
                    'System upgrade',
                    'Policy update'
                ]
                
                action = Action(
                    title=f"{random.choice(action_verbs)} {incident.category} - {incident.subcategory}",
                    description=f"Action to address {incident.subcategory} issue through {random.choice(improvement_types)}.",
                    type=random.choice(action_types),
                    priority=random.choice(priorities),
                    status=status,
                    date=action_date,
                    due_date=due_date,
                    incident=incident,
                    assignee=admin
                )
                
                if status == 'Completed':
                    action.completion_date = action_date + timedelta(days=random.randint(7, 30))
                
                db.session.add(action)

        # Create metrics
        print("Creating metrics...")
        metric_types = {
            'Health': ['Incident Rate', 'Training Coverage', 'Health Check Completion'],
            'Safety': ['Safety Incidents', 'Near Miss Reports', 'Safety Training Hours'],
            'Quality': ['Defect Rate', 'Customer Satisfaction', 'Process Compliance'],
            'Environment': ['Energy Usage', 'Waste Generation', 'Water Consumption']
        }
        
        # Create metrics for the last 12 months
        for month in range(12):
            for category in categories:
                for metric_type in metric_types[category]:
                    metric = HSQEMetric(
                        category=category,
                        metric_type=metric_type,
                        value=random.uniform(60, 100),
                        unit='%',
                        target=75.0,
                        notes=f"Monthly {metric_type.lower()} measurement",
                        date=datetime.now() - timedelta(days=30 * month),
                        created_by=admin
                    )
                    db.session.add(metric)

        try:
            db.session.commit()
            print("Demo data added successfully!")
        except Exception as e:
            print(f"Error adding demo data: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_demo_data()
