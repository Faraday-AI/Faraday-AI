import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService

def create_admin_user():
    db = SessionLocal()
    auth_service = AuthService()
    
    # Check if admin user already exists
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if admin:
        print("Admin user already exists")
        return
    
    # Create admin user
    admin = User(
        email="admin@example.com",
        name="Admin",
        hashed_password=auth_service.get_password_hash("admin"),
        is_active=True
    )
    
    db.add(admin)
    db.commit()
    print("Admin user created successfully")
    print("Email: admin@example.com")
    print("Password: admin")

if __name__ == "__main__":
    create_admin_user() 