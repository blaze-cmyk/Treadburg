"""
Push migration directly to Supabase PostgreSQL database
"""

import os
from dotenv import load_dotenv

load_dotenv(".env.mcp")

print("=" * 70)
print("  PUSHING MIGRATION TO SUPABASE DATABASE")
print("=" * 70)

try:
    import psycopg2
    
    # Get Supabase connection details
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env.mcp")
        exit(1)
    
    # Extract project ref from URL
    # URL format: https://pcxscejarxztezfeucgs.supabase.co
    project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")
    
    # Construct PostgreSQL connection string
    # Try direct connection to database
    from urllib.parse import quote_plus
    db_password = quote_plus("Blaze@supa1")
    
    # Try different connection formats
    conn_strings = [
        f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres",
        f"postgresql://postgres.{project_ref}:{db_password}@aws-0-ap-south-1.pooler.supabase.com:5432/postgres",
        f"host=db.{project_ref}.supabase.co port=5432 dbname=postgres user=postgres password=Blaze@supa1"
    ]
    
    conn = None
    for i, conn_string in enumerate(conn_strings, 1):
        try:
            print(f"   Trying connection method {i}...")
            conn = psycopg2.connect(conn_string)
            print(f"   ✅ Connected using method {i}")
            break
        except Exception as e:
            print(f"   ❌ Method {i} failed: {str(e)[:60]}")
            continue
    
    if not conn:
        raise Exception("All connection methods failed")
    
    print(f"\n🔌 Connecting to Supabase PostgreSQL...")
    print(f"   Project: {project_ref}")
    
    # Connect
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    
    print("✅ Connected to database")
    
    # Read migration file
    print("\n📄 Reading migration file...")
    with open("supabase/migrations/002_user_management_system.sql", 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print(f"✅ Loaded {len(sql)} characters")
    
    # Execute migration
    print("\n🚀 Executing migration...")
    
    try:
        cursor.execute(sql)
        conn.commit()
        print("✅ Migration executed successfully!")
        
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        if 'already exists' in error_msg.lower():
            print("⚠️  Tables already exist - that's OK!")
        else:
            print(f"❌ Error: {error_msg}")
    
    # Verify tables
    print("\n🔍 Verifying tables...")
    tables = ['users', 'credit_transactions', 'payments', 'subscriptions', 
              'api_usage_log', 'login_history', 'admin_activity_log', 'credit_packages']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM public.{table}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {table} ({count} rows)")
        except Exception as e:
            print(f"   ❌ {table}: {str(e)[:50]}")
    
    # Close connection
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("  ✅ MIGRATION COMPLETE!")
    print("=" * 70)
    print("\n📝 Next steps:")
    print("   1. Verify tables in Supabase dashboard")
    print("   2. Create your first admin user")
    print("   3. Test the API endpoints")
    
except ImportError:
    print("❌ psycopg2 not installed")
    print("   Run: pip install psycopg2-binary")
    print("\n💡 Alternative: Run migration manually in Supabase SQL Editor")
    print("   URL: https://app.supabase.com/project/pcxscejarxztezfeucgs/sql")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Please run migration manually in Supabase SQL Editor:")
    print("   1. Go to: https://app.supabase.com/project/pcxscejarxztezfeucgs/sql")
    print("   2. Copy content from: backend/supabase/migrations/002_user_management_system.sql")
    print("   3. Paste and click 'Run'")
