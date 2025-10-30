import sys
sys.path.insert(0, r'C:\Users\KIRA\PycharmProjects\care')

from database import SessionLocal
from models import User, Patient, Service, Appointment, Payment, AppointmentState
from auth import get_password_hash
from datetime import date, time
from decimal import Decimal

print("🚀 Starting database seeding...")

db = SessionLocal()

try:
    # Create users
    print("Creating users...")
    admin = User(username="admin", password_hash=get_password_hash("admin123"), role="admin", is_active=True)
    staff1 = User(username="staff1", password_hash=get_password_hash("staff123"), role="staff", is_active=True)
    db.add_all([admin, staff1])
    db.commit()
    print(f"✓ Created 2 users")
    
    # Create services
    print("Creating services...")
    services = [
        Service(nom="Consultation", description="Consultation dentaire", prix_base=Decimal("50.00"), actif=True),
        Service(nom="Détartrage", description="Nettoyage dentaire", prix_base=Decimal("80.00"), actif=True),
        Service(nom="Plombage", description="Traitement carie", prix_base=Decimal("120.00"), actif=True),
        Service(nom="Couronne", description="Couronne dentaire", prix_base=Decimal("400.00"), actif=True),
        Service(nom="Implant", description="Implant dentaire", prix_base=Decimal("1500.00"), actif=True),
    ]
    db.add_all(services)
    db.commit()
    db.refresh(services[0])
    db.refresh(services[1])
    db.refresh(services[2])
    db.refresh(services[3])
    db.refresh(services[4])
    print(f"✓ Created {len(services)} services")
    
    # Create patients
    print("Creating patients...")
    patients = [
        Patient(nom="Ben Salah", prenom="Ahmed", phone="21612345678", email="ahmed.bensalah@email.tn", date_naissance=date(1980, 5, 15)),
        Patient(nom="Trabelsi", prenom="Fatima", phone="21698765432", email="fatima.t@email.tn", date_naissance=date(1992, 8, 22)),
        Patient(nom="Nasri", prenom="Mohamed", phone="21654321098", email="mohamed.n@email.tn", date_naissance=date(1975, 3, 10)),
        Patient(nom="Karoui", prenom="Amina", phone="21687654321", email="amina.k@email.tn", date_naissance=date(1988, 11, 5)),
        Patient(nom="Hamdi", prenom="Karim", phone="21623456789", email="karim.h@email.tn", date_naissance=date(1995, 7, 18)),
    ]
    db.add_all(patients)
    db.commit()
    # Refresh to get IDs
    for patient in patients:
        db.refresh(patient)
    print(f"✓ Created {len(patients)} patients")
    
    # Create appointments with proper enum values
    print("Creating appointments...")
    appointments = [
        Appointment(patient_id=patients[0].id, service_id=services[0].id, date=date(2025, 10, 28), heure=time(9, 0), prix=Decimal("50"), verse=Decimal("50"), reste=Decimal("0"), etat=AppointmentState.valide),
        Appointment(patient_id=patients[1].id, service_id=services[1].id, date=date(2025, 10, 28), heure=time(10, 30), prix=Decimal("80"), verse=Decimal("40"), reste=Decimal("40"), etat=AppointmentState.en_attente),
        Appointment(patient_id=patients[2].id, service_id=services[2].id, date=date(2025, 10, 29), heure=time(14, 0), prix=Decimal("120"), verse=Decimal("0"), reste=Decimal("120"), etat=AppointmentState.en_attente),
        Appointment(patient_id=patients[3].id, service_id=services[3].id, date=date(2025, 11, 5), heure=time(11, 0), prix=Decimal("400"), verse=Decimal("200"), reste=Decimal("200"), etat=AppointmentState.valide),
        Appointment(patient_id=patients[4].id, service_id=services[0].id, date=date(2025, 11, 10), heure=time(15, 30), prix=Decimal("50"), verse=Decimal("0"), reste=Decimal("50"), etat=AppointmentState.en_attente),
    ]
    db.add_all(appointments)
    db.commit()
    print(f"✓ Created {len(appointments)} appointments")
    
    print("\n" + "="*50)
    print("✅ Database seeding completed successfully!")
    print("="*50)
    print("\nLogin credentials:")
    print("  👤 Admin: admin / admin123")
    print("  👤 Staff: staff1 / staff123")
    print("\n🌐 Start the app with: python main.py")
    print("📱 Then open: http://localhost:8000")
    
except Exception as e:
    print(f"\n❌ Error during seeding: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
