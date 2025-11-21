"""
Update avatar image URLs to use DiceBear Avatars service.

This script updates the image_url field in the avatars table to use
DiceBear Avatars API URLs instead of local file paths.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def update_avatar_urls():
    """Update avatar image URLs to DiceBear URLs."""
    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is required but not set. "
            "Please ensure the .env file has DATABASE_URL, "
            "or set DATABASE_URL in docker-compose.yml environment section."
        )
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check which table exists and has data
        # Try beta_avatars first (used by beta teacher dashboard)
        result = session.execute(text("SELECT COUNT(*) FROM beta_avatars"))
        beta_count = result.scalar()
        
        if beta_count > 0:
            print(f"🔄 Found {beta_count} avatars in beta_avatars table")
            result = session.execute(text("SELECT id, type, image_url FROM beta_avatars ORDER BY created_at"))
            avatars = result.fetchall()
            table_name = "beta_avatars"
            id_field = "id"
        else:
            # Try regular avatars table
            result = session.execute(text("SELECT COUNT(*) FROM avatars"))
            avatar_count = result.scalar()
            if avatar_count > 0:
                print(f"🔄 Found {avatar_count} avatars in avatars table")
                result = session.execute(text("SELECT id, type, url FROM avatars ORDER BY id"))
                avatars = result.fetchall()
                table_name = "avatars"
                id_field = "id"
                url_field = "url"
            else:
                print("⚠️  No avatars found in database")
                return
        
        if not avatars:
            print("⚠️  No avatars found in database")
            return
        
        print(f"🔄 Found {len(avatars)} avatars to update")
        
        # DiceBear style mapping based on avatar type
        style_map = {
            'STATIC': 'avataaars',      # Professional, friendly avatars
            'ANIMATED': 'lorelei',      # Animated-style avatars
            'THREE_D': 'bottts',        # 3D robot-style avatars
            '3D': 'bottts'              # Alternative 3D naming
        }
        
        updated_count = 0
        
        for avatar_row in avatars:
            if table_name == "beta_avatars":
                avatar_id, avatar_type, current_url = avatar_row
                url_field = "image_url"
            else:
                avatar_id, avatar_type, current_url = avatar_row
                url_field = "url"
            
            # Determine DiceBear style based on avatar type
            avatar_type_upper = str(avatar_type).upper() if avatar_type else 'STATIC'
            style = style_map.get(avatar_type_upper, 'avataaars')
            
            # Create unique seed based on avatar ID to ensure consistent appearance
            # For UUIDs, use the string representation
            seed = f"faraday-avatar-{str(avatar_id)}"
            
            # Generate DiceBear URL
            # Using SVG format for crisp rendering at any size
            dicebear_url = f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}&size=200"
            
            # Update the avatar
            if table_name == "beta_avatars":
                session.execute(text(f"""
                    UPDATE {table_name} 
                    SET {url_field} = :new_url
                    WHERE id = :avatar_id
                """), {
                    'new_url': dicebear_url,
                    'avatar_id': avatar_id
                })
            else:
                session.execute(text(f"""
                    UPDATE {table_name} 
                    SET {url_field} = :new_url
                    WHERE id = :avatar_id
                """), {
                    'new_url': dicebear_url,
                    'avatar_id': avatar_id
                })
            
            print(f"  ✅ Updated avatar {avatar_id} ({avatar_type_upper}): {dicebear_url}")
            updated_count += 1
        
        # Commit changes
        session.commit()
        print(f"\n✅ Successfully updated {updated_count} avatar URLs to DiceBear")
        print("\n📝 Note: DiceBear URLs are external and require internet connection to load")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error updating avatar URLs: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("🔄 Updating avatar image URLs to DiceBear Avatars...")
    update_avatar_urls()
    print("✅ Update complete!")

