import sys
sys.path.insert(0, r'C:\Users\KIRA\PycharmProjects\care')

from database import SessionLocal
from models import Patient
from datetime import date

print("🚀 Adding patients requiring validation...")

db = SessionLocal()

try:
    # Create patients requiring validation
    patients = [
        Patient(
            nom="Gharbi",
            prenom="Sami",
            phone="21655667788",
            email="sami.g@email.tn",
            date_naissance=date(1990, 4, 12),
            requires_validation=True,
            notes="Nouveau patient - nécessite validation"
        ),
        Patient(
            nom="Mejri",
            prenom="Leila",
            phone="21644556677",
            email="leila.m@email.tn",
            date_naissance=date(1985, 9, 25),
            requires_validation=True,
            notes="Nouveau patient - nécessite validation"
        ),
        Patient(
            nom="Bouazizi",
            prenom="Riadh",
            phone="21633445566",
            email="riadh.b@email.tn",
            date_naissance=date(1978, 6, 8),
            requires_validation=True,
            notes="Nouveau patient - nécessite validation"
        ),
    ]

    db.add_all(patients)
    db.commit()

    print(f"✅ Successfully added {len(patients)} patients requiring validation!")
    print("\n📋 Patients added:")
    for p in patients:
        db.refresh(p)
        print(f"   • {p.prenom} {p.nom} (ID: {p.id}) - {p.phone}")

    print("\n🌐 Visit: http://127.0.0.1:8000/clients/valider")

except Exception as e:
    print(f"\n❌ Error: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()

