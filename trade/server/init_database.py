"""
Initialize the database - Create all tables
Run this script to set up the database before starting the server
"""
from database import init_db

if __name__ == "__main__":
    print("🔧 Initializing TradeBerg database...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
        print("📊 Tables created:")
        print("   - chats")
        print("   - messages")
        print("   - users")
        print("\n🚀 You can now start the backend server with: python app.py")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
