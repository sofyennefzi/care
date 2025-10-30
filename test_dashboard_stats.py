"""
Test dashboard stats generation
"""
from database import SessionLocal
from stats import get_dashboard_stats
import json

print("=" * 60)
print("TESTING DASHBOARD STATS")
print("=" * 60)

db = SessionLocal()

try:
    stats = get_dashboard_stats(db)

    print(f"\n✅ Stats generated successfully!")
    print(f"\nBasic stats:")
    print(f"   Total patients: {stats['total_patients']}")
    print(f"   Total RDV: {stats['total_rdv']}")
    print(f"   RDV passés: {stats['rdv_passes']}")
    print(f"   RDV futurs: {stats['rdv_futurs']}")
    print(f"   Revenu total: {stats['revenu_total']}")
    print(f"   Caisse du jour: {stats['caisse_jour']}")

    print(f"\nRépartition par état:")
    for state, count in stats['repartition_etat'].items():
        print(f"   {state}: {count}")

    print(f"\nRDV par jour de la semaine:")
    rdv_par_jour = stats['rdv_par_jour']
    for day, count in rdv_par_jour.items():
        print(f"   {day}: {count}")

    # Check if there's any data in rdv_par_jour
    total_weekly = sum(rdv_par_jour.values())
    print(f"\n📊 Total RDV this week: {total_weekly}")

    print(f"\nTop 5 services:")
    top_services = stats['top_services']
    print(f"   Number of services: {len(top_services)}")
    for i, service in enumerate(top_services[:5], 1):
        print(f"   {i}. {service['nom']}: {service['count']} RDV")

    print(f"\n📈 JSON data for charts:")
    print(f"RDV par jour: {json.dumps(rdv_par_jour, indent=2)}")
    print(f"Top services: {json.dumps(top_services, indent=2)}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 60)
