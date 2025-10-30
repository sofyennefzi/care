import sys
sys.path.insert(0, r'C:\Users\KIRA\PycharmProjects\care')

from database import SessionLocal
from models import User, Patient, Service, Appointment, Payment

print("🗑️ Clearing database...")

db = SessionLocal()

try:
    # Delete all data in correct order (respecting foreign keys)
    deleted_payments = db.query(Payment).delete()
    deleted_appointments = db.query(Appointment).delete()
    deleted_patients = db.query(Patient).delete()
    deleted_services = db.query(Service).delete()
    deleted_users = db.query(User).delete()

    db.commit()

    print(f"✓ Deleted {deleted_payments} payments")
    print(f"✓ Deleted {deleted_appointments} appointments")
    print(f"✓ Deleted {deleted_patients} patients")
    print(f"✓ Deleted {deleted_services} services")
    print(f"✓ Deleted {deleted_users} users")
    print("\n✅ Database cleared successfully!")
    print("Now run: python quick_seed.py")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()

