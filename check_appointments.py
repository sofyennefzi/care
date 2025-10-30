"""
Check database for appointments
"""
from database import SessionLocal, engine
from models import Appointment, Patient, Service
from datetime import datetime, timedelta

print("=" * 60)
print("CHECKING DATABASE FOR APPOINTMENTS")
print("=" * 60)

db = SessionLocal()

try:
    # Count total appointments
    total_appointments = db.query(Appointment).count()
    print(f"\n✅ Total appointments in database: {total_appointments}")

    if total_appointments == 0:
        print("\n⚠️ WARNING: No appointments found in database!")
        print("   You need to create some test data first.")
        print("   Run: python seed.py")
    else:
        # Show first 5 appointments
        print(f"\nFirst 5 appointments:")
        appointments = db.query(Appointment).limit(5).all()

        for i, appt in enumerate(appointments, 1):
            patient = db.query(Patient).filter(Patient.id == appt.patient_id).first()
            service = db.query(Service).filter(Service.id == appt.service_id).first()

            patient_name = f"{patient.prenom} {patient.nom}" if patient else "Unknown"
            service_name = service.nom if service else "Unknown"

            print(f"{i}. ID: {appt.id}")
            print(f"   Patient: {patient_name}")
            print(f"   Service: {service_name}")
            print(f"   Date: {appt.date}")
            print(f"   Heure: {appt.heure}")
            print(f"   État: {appt.etat.value}")
            print()

        # Check appointments in current month
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        next_month = start_of_month.replace(day=28) + timedelta(days=4)
        end_of_month = next_month.replace(day=1)

        current_month_count = db.query(Appointment).filter(
            Appointment.date >= start_of_month,
            Appointment.date < end_of_month
        ).count()

        print(f"\n📅 Appointments in current month ({start_of_month} to {end_of_month}): {current_month_count}")

        # Check for October 2025 specifically
        oct_start = datetime(2025, 10, 1).date()
        oct_end = datetime(2025, 11, 1).date()

        oct_count = db.query(Appointment).filter(
            Appointment.date >= oct_start,
            Appointment.date < oct_end
        ).count()

        print(f"📅 Appointments in October 2025: {oct_count}")

        if oct_count > 0:
            print(f"\nSample appointments in October 2025:")
            oct_appts = db.query(Appointment).filter(
                Appointment.date >= oct_start,
                Appointment.date < oct_end
            ).limit(3).all()

            for appt in oct_appts:
                patient = db.query(Patient).filter(Patient.id == appt.patient_id).first()
                service = db.query(Service).filter(Service.id == appt.service_id).first()
                patient_name = f"{patient.prenom} {patient.nom}" if patient else "Unknown"
                service_name = service.nom if service else "Unknown"
                print(f"   - {appt.date} at {appt.heure}: {patient_name} - {service_name}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 60)

