from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from datetime import date
from decimal import Decimal
from typing import Optional
from models import Patient, Appointment, Payment, Service, AppointmentState


def get_dashboard_stats(db: Session, date_from: Optional[date] = None, date_to: Optional[date] = None) -> dict:
    """Get comprehensive dashboard statistics"""

    # Basic counts
    total_patients = db.query(func.count(Patient.id)).scalar()

    query = db.query(Appointment)
    if date_from:
        query = query.filter(Appointment.date >= date_from)
    if date_to:
        query = query.filter(Appointment.date <= date_to)

    total_rdv = query.count()

    today = date.today()
    rdv_passes = query.filter(Appointment.date < today).count()
    rdv_futurs = query.filter(Appointment.date >= today).count()

    # Revenue - sum all payments
    payment_query = db.query(func.sum(Payment.montant))
    if date_from or date_to:
        payment_query = payment_query.join(Appointment)
        if date_from:
            payment_query = payment_query.filter(Appointment.date >= date_from)
        if date_to:
            payment_query = payment_query.filter(Appointment.date <= date_to)

    revenu_total = payment_query.scalar() or Decimal("0")

    # Caisse du jour
    from crud import get_caisse_du_jour
    caisse_jour = get_caisse_du_jour(db)

    # Répartition par état
    repartition_etat = {}
    for state in AppointmentState:
        count_query = query.filter(Appointment.etat == state)
        repartition_etat[state.value] = count_query.count()

    # RDV par jour de la semaine (0=Monday, 6=Sunday)
    rdv_par_jour = {
        "Lundi": 0, "Mardi": 0, "Mercredi": 0, "Jeudi": 0,
        "Vendredi": 0, "Samedi": 0, "Dimanche": 0
    }

    # Get appointments grouped by day of week (MySQL compatible)
    # DAYOFWEEK returns 1=Sunday, 2=Monday, ..., 7=Saturday
    appointments_by_day = db.query(
        func.dayofweek(Appointment.date).label('day_of_week'),
        func.count(Appointment.id).label('count')
    ).filter(
        and_(
            Appointment.date >= date_from if date_from else True,
            Appointment.date <= date_to if date_to else True
        )
    ).group_by(func.dayofweek(Appointment.date)).all()

    # MySQL DAYOFWEEK: 1=Sunday, 2=Monday, 3=Tuesday, ..., 7=Saturday
    day_mapping = {
        2: "Lundi", 3: "Mardi", 4: "Mercredi", 5: "Jeudi",
        6: "Vendredi", 7: "Samedi", 1: "Dimanche"
    }

    for day_num, count in appointments_by_day:
        day_name = day_mapping.get(int(day_num), "Lundi")
        rdv_par_jour[day_name] = count

    # Top 5 services
    top_services_query = db.query(
        Service.nom,
        func.count(Appointment.id).label('count')
    ).join(Appointment).filter(
        and_(
            Appointment.date >= date_from if date_from else True,
            Appointment.date <= date_to if date_to else True
        )
    ).group_by(Service.id, Service.nom).order_by(func.count(Appointment.id).desc()).limit(5)

    top_services = [{"nom": nom, "count": count} for nom, count in top_services_query.all()]

    return {
        "total_patients": total_patients,
        "total_rdv": total_rdv,
        "rdv_passes": rdv_passes,
        "rdv_futurs": rdv_futurs,
        "revenu_total": float(revenu_total),
        "caisse_jour": float(caisse_jour),
        "repartition_etat": repartition_etat,
        "rdv_par_jour": rdv_par_jour,
        "top_services": top_services
    }
