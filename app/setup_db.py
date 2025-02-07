from app import create_app, db
from app.models import User
import os
import sqlite3

def setup_database():
    print("\n=== Starting Database Setup ===")
    
    # Create Flask app
    app = create_app()
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'hsqe.db'))
    
    print(f"\nDatabase Configuration:")
    print(f"- Path: {db_path}")
    print(f"- URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        print(f"\nRemoving existing database...")
        os.remove(db_path)
        print("Existing database removed")
    
    with app.app_context():
        print("\nCreating database tables...")
        db.create_all()
        print("Database tables created")
        
        # Verify tables were created
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("\nVerifying database tables:")
            for table in tables:
                print(f"- {table[0]}")
            conn.close()
        except Exception as e:
            print(f"Error checking tables: {str(e)}")
        
        print("\nCreating admin user...")
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
            print("Admin user committed to database")
            
            # Verify admin user
            admin_check = User.query.filter_by(username='admin').first()
            if admin_check:
                print("\nAdmin user verified in database:")
                print(f"- ID: {admin_check.id}")
                print(f"- Username: {admin_check.username}")
                print(f"- Role: {admin_check.role}")
                print(f"- Is Admin: {admin_check.is_admin}")
                print(f"- Password Hash: {admin_check.password_hash}")
                
                # Test password verification
                test_password = 'admin'
                is_valid = admin_check.check_password(test_password)
                print(f"\nPassword verification test: {'SUCCESS' if is_valid else 'FAILED'}")
                
                # Query database directly
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user WHERE username=?", ('admin',))
                user_row = cursor.fetchone()
                print("\nDirect database query result:")
                print(f"- Row: {user_row}")
                conn.close()
            else:
                print("ERROR: Admin user not found after creation!")
                
            # Verify database file
            if os.path.exists(db_path):
                print(f"\nDatabase file verified:")
                print(f"- Path: {db_path}")
                print(f"- Size: {os.path.getsize(db_path)} bytes")
                print(f"- Permissions: {oct(os.stat(db_path).st_mode)[-3:]}")
            else:
                print(f"\nERROR: Database file not found at {db_path}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()
            raise e

if __name__ == '__main__':
    setup_database()
