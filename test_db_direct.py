import sys
sys.path.insert(0, r'C:\Users\KIRA\PycharmProjects\care')

# Direct database test - bypass the API
from database import SessionLocal
from crud import get_services

print("Testing services directly from database...")
print("="*60)

try:
    db = SessionLocal()
    services = get_services(db, active_only=True)
    
    print(f"✅ Found {len(services)} active services:")
    for svc in services:
        print(f"   - {svc.nom}: {svc.prix_base} TND (actif={svc.actif})")
    
    # Also try getting ALL services
    all_services = get_services(db, active_only=False)
    print(f"\n📋 Total services in database: {len(all_services)}")
    
    db.close()
    print("\n" + "="*60)
    print("✅ DATABASE TEST PASSED!")
    print("\nIf this works but the API doesn't, the problem is:")
    print("  1. Authentication issue")
    print("  2. Pydantic schema serialization issue")
    print("  3. FastAPI routing issue")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

