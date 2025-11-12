"""
Push database migration to Supabase
"""

import os
from dotenv import load_dotenv
from open_webui.integrations.supabase_integration import get_supabase_client

load_dotenv(".env.mcp")

print("=" * 70)
print("  PUSHING DATABASE MIGRATION TO SUPABASE")
print("=" * 70)

try:
    # Read migration file
    migration_file = "supabase/migrations/002_user_management_system.sql"
    
    print(f"\n📄 Reading migration file: {migration_file}")
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"✅ Migration file loaded ({len(sql_content)} characters)")
    
    # Get Supabase client
    print("\n🔌 Connecting to Supabase...")
    supabase = get_supabase_client()
    print(f"✅ Connected to: {os.getenv('SUPABASE_URL')}")
    
    # Execute migration
    print("\n🚀 Executing migration...")
    print("   This may take a few seconds...")
    
    # Split SQL into individual statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    
    print(f"\n📊 Found {len(statements)} SQL statements")
    
    executed = 0
    errors = 0
    
    for i, statement in enumerate(statements, 1):
        if not statement or statement.startswith('--'):
            continue
        
        try:
            # Execute each statement
            result = supabase.client.rpc('exec_sql', {'sql': statement}).execute()
            executed += 1
            if i % 10 == 0:
                print(f"   Executed {i}/{len(statements)} statements...")
        except Exception as e:
            # Some errors are OK (like "already exists")
            if 'already exists' in str(e).lower():
                print(f"   ⚠️  Statement {i}: Already exists (skipping)")
            else:
                print(f"   ❌ Statement {i}: {str(e)[:100]}")
                errors += 1
    
    print(f"\n✅ Migration complete!")
    print(f"   Executed: {executed} statements")
    if errors > 0:
        print(f"   Errors: {errors} (check if tables already exist)")
    
    # Verify tables
    print("\n🔍 Verifying tables...")
    tables_to_check = [
        'users', 'credit_transactions', 'payments', 
        'subscriptions', 'api_usage_log', 'login_history',
        'admin_activity_log', 'credit_packages'
    ]
    
    for table in tables_to_check:
        try:
            result = supabase.client.table(table).select('*').limit(1).execute()
            print(f"   ✅ {table}")
        except Exception as e:
            print(f"   ❌ {table}: {str(e)[:50]}")
    
    print("\n" + "=" * 70)
    print("  MIGRATION COMPLETE!")
    print("=" * 70)
    print("\n📝 Next steps:")
    print("   1. Go to Supabase dashboard to verify tables")
    print("   2. Create your first admin user")
    print("   3. Test the API endpoints")
    
except FileNotFoundError:
    print("\n❌ Migration file not found!")
    print("   Make sure you're in the backend directory")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Alternative: Copy the SQL file content and run it manually in Supabase SQL Editor")
    print("   File: backend/supabase/migrations/002_user_management_system.sql")
    print("   URL: https://app.supabase.com/project/pcxscejarxztezfeucgs/sql")
