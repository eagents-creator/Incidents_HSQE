from app import create_app, db
from app.models import User

def create_admin_user():
    print("Creating admin user...")
    
    app = create_app()
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists")
            return
        
        # Create new admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin')
        admin.set_role('admin')
        
        try:
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
            print("Username: admin")
            print("Password: admin")
        except Exception as e:
            print(f"Error creating admin user: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_admin_user()
