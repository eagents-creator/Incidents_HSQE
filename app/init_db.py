from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Create all database tables
    db.create_all()
    
    # Delete existing admin user if exists
    admin = User.query.filter_by(username='admin').first()
    if admin:
        db.session.delete(admin)
        db.session.commit()
        print("Existing admin user deleted")
    
    # Create new admin user
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('admin')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully with password: admin")
