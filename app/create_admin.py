from app import create_app, db
from app.models import User
import os

def create_admin():
    print("Starting admin user creation...")
    app = create_app()
    
    # Get absolute path to database
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'hsqe.db'))
    print(f"Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database file does not exist at {db_path}")
    else:
        print(f"Database file exists at {db_path}")
        print(f"File size: {os.path.getsize(db_path)} bytes")
        print(f"File permissions: {oct(os.stat(db_path).st_mode)[-3:]}")
    
    with app.app_context():
        print("\nCreating database tables...")
        db.create_all()
        print("Database tables created")
        
        print("\nChecking for existing admin user...")
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user exists, updating password...")
            admin.set_password('admin')
            admin.set_role('admin')
        else:
            print("Creating new admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin')
            admin.set_role('admin')
            db.session.add(admin)
        
        try:
            db.session.commit()
            print("Changes committed to database")
            
            # List all users in database
            print("\nAll users in database:")
            users = User.query.all()
            for user in users:
                print(f"- {user.username} (id: {user.id}, role: {user.role}, is_admin: {user.is_admin})")
            
            # Verify admin exists and has correct permissions
            print("\nVerifying admin user...")
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"Admin user verified:")
                print(f"- ID: {admin.id}")
                print(f"- Username: {admin.username}")
                print(f"- Role: {admin.role}")
                print(f"- Is Admin: {admin.is_admin}")
                print(f"- Password Hash: {admin.password_hash}")
                
                # Test password verification
                test_password = 'admin'
                is_valid = admin.check_password(test_password)
                print(f"\nPassword verification test: {'SUCCESS' if is_valid else 'FAILED'}")
            else:
                print("ERROR: Admin user not found after creation!")
        except Exception as e:
            print(f"Error committing changes: {str(e)}")
            db.session.rollback()
            raise e

if __name__ == '__main__':
    create_admin()
