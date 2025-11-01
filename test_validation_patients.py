"""
Quick test to verify validation patients page
"""
import sys
sys.path.insert(0, r'C:\Users\KIRA\PycharmProjects\care')

from database import SessionLocal
from crud import get_patients_requiring_validation

db = SessionLocal()

try:
    patients = get_patients_requiring_validation(db)

    print(f"\n📊 Found {len(patients)} patients requiring validation:\n")

    if patients:
        for p in patients:
            print(f"   ✓ ID: {p.id}")
            print(f"     Nom: {p.prenom} {p.nom}")
            print(f"     Téléphone: {p.phone}")
            print(f"     Email: {p.email}")
            print(f"     Date naissance: {p.date_naissance}")
            print(f"     Notes: {p.notes}")
            print()

        print(f"✅ The page http://127.0.0.1:8000/clients/valider should now show {len(patients)} patients!")
    else:
        print("❌ No patients found requiring validation")
        print("This is why the page shows 'Aucun client en attente de validation'")

finally:
    db.close()

