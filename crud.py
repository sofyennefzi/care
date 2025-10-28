from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal
from models import User, Patient, Service, Appointment, Payment, AuditLog, AppointmentState
import schemas


# Audit logging
def create_audit_log(db: Session, user_id: Optional[int], action: str, target_table: str, target_id: Optional[int], metadata: dict = None):
    log = AuditLog(
        user_id=user_id,
        action=action,
        target_table=target_table,
        target_id=target_id,
        metadata=metadata
    )
    db.add(log)
    db.commit()


# User CRUD
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> User:
    from auth import get_password_hash
    db_user = User(
        username=user.username,
        password_hash=get_password_hash(user.password),
        role=user.role,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Patient CRUD
def get_patients(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Patient]:
    query = db.query(Patient)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Patient.nom.like(search_term),
                Patient.prenom.like(search_term),
                Patient.phone.like(search_term),
                Patient.email.like(search_term)
            )
        )
    return query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()


def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id).first()


def create_patient(db: Session, patient: schemas.PatientCreate, user_id: Optional[int] = None) -> Patient:
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    create_audit_log(db, user_id, "CREATE", "patients", db_patient.id)
    return db_patient


def update_patient(db: Session, patient_id: int, patient: schemas.PatientUpdate, user_id: Optional[int] = None) -> Optional[Patient]:
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None

    update_data = patient.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)

    db.commit()
    db.refresh(db_patient)
    create_audit_log(db, user_id, "UPDATE", "patients", patient_id, update_data)
    return db_patient


def delete_patient(db: Session, patient_id: int, user_id: Optional[int] = None) -> bool:
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return False
    db.delete(db_patient)
    db.commit()
    create_audit_log(db, user_id, "DELETE", "patients", patient_id)
    return True


def get_patients_requiring_validation(db: Session) -> List[Patient]:
    return db.query(Patient).filter(Patient.requires_validation == True).all()


# Service CRUD
def get_services(db: Session, active_only: bool = True) -> List[Service]:
    query = db.query(Service)
    if active_only:
        query = query.filter(Service.actif == True)
    return query.all()


def get_service(db: Session, service_id: int) -> Optional[Service]:
    return db.query(Service).filter(Service.id == service_id).first()


# Appointment CRUD
def get_appointments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    etat: Optional[AppointmentState] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    patient_id: Optional[int] = None
) -> List[Appointment]:
    query = db.query(Appointment)

    if search:
        search_term = f"%{search}%"
        query = query.join(Patient).filter(
            or_(
                Patient.nom.like(search_term),
                Patient.prenom.like(search_term)
            )
        )

    if etat:
        query = query.filter(Appointment.etat == etat)

    if date_from:
        query = query.filter(Appointment.date >= date_from)

    if date_to:
        query = query.filter(Appointment.date <= date_to)

    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)

    return query.order_by(Appointment.date.desc(), Appointment.heure.desc()).offset(skip).limit(limit).all()


def get_appointment(db: Session, appointment_id: int) -> Optional[Appointment]:
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()


def check_appointment_overlap(db: Session, patient_id: int, date_val: date, heure_val: time, exclude_id: Optional[int] = None) -> bool:
    """Check if patient has overlapping appointment"""
    query = db.query(Appointment).filter(
        and_(
            Appointment.patient_id == patient_id,
            Appointment.date == date_val,
            Appointment.heure == heure_val,
            Appointment.etat != AppointmentState.annule
        )
    )
    if exclude_id:
        query = query.filter(Appointment.id != exclude_id)

    return query.first() is not None


def create_appointment(db: Session, appointment: schemas.AppointmentCreate, user_id: Optional[int] = None) -> Appointment:
    # Check for overlap
    if check_appointment_overlap(db, appointment.patient_id, appointment.date, appointment.heure):
        raise ValueError("Ce patient a déjà un rendez-vous à cette date et heure")

    reste_val = appointment.prix - appointment.verse
    db_appointment = Appointment(**appointment.model_dump(), reste=reste_val)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    create_audit_log(db, user_id, "CREATE", "appointments", db_appointment.id)
    return db_appointment


def update_appointment(db: Session, appointment_id: int, appointment: schemas.AppointmentUpdate, user_id: Optional[int] = None) -> Optional[Appointment]:
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None

    update_data = appointment.model_dump(exclude_unset=True)

    # Check for overlap if date or time changed
    if 'date' in update_data or 'heure' in update_data:
        new_date = update_data.get('date', db_appointment.date)
        new_heure = update_data.get('heure', db_appointment.heure)
        patient_id = update_data.get('patient_id', db_appointment.patient_id)

        if check_appointment_overlap(db, patient_id, new_date, new_heure, appointment_id):
            raise ValueError("Ce patient a déjà un rendez-vous à cette date et heure")

    for field, value in update_data.items():
        setattr(db_appointment, field, value)

    # Recalculate reste
    db_appointment.reste = db_appointment.prix - db_appointment.verse

    db.commit()
    db.refresh(db_appointment)
    create_audit_log(db, user_id, "UPDATE", "appointments", appointment_id, update_data)
    return db_appointment


def delete_appointment(db: Session, appointment_id: int, user_id: Optional[int] = None) -> bool:
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return False
    db.delete(db_appointment)
    db.commit()
    create_audit_log(db, user_id, "DELETE", "appointments", appointment_id)
    return True


def get_today_appointments(db: Session) -> List[Appointment]:
    today = date.today()
    return db.query(Appointment).filter(Appointment.date == today).order_by(Appointment.heure).all()


# Payment CRUD
def get_payments_for_appointment(db: Session, appointment_id: int) -> List[Payment]:
    return db.query(Payment).filter(Payment.appointment_id == appointment_id).order_by(Payment.created_at).all()


def create_payment(db: Session, payment: schemas.PaymentCreate, user_id: Optional[int] = None) -> Payment:
    db_appointment = get_appointment(db, payment.appointment_id)
    if not db_appointment:
        raise ValueError("Rendez-vous introuvable")

    if db_appointment.etat == AppointmentState.annule:
        raise ValueError("Impossible d'ajouter un paiement à un rendez-vous annulé")

    db_payment = Payment(**payment.model_dump())
    db.add(db_payment)

    # Update appointment verse
    total_verse = db.query(func.sum(Payment.montant)).filter(Payment.appointment_id == payment.appointment_id).scalar() or Decimal("0")
    total_verse += payment.montant
    db_appointment.verse = total_verse
    db_appointment.reste = db_appointment.prix - total_verse

    db.commit()
    db.refresh(db_payment)
    create_audit_log(db, user_id, "CREATE", "payments", db_payment.id, {"appointment_id": payment.appointment_id, "montant": float(payment.montant)})
    return db_payment


def get_caisse_du_jour(db: Session) -> Decimal:
    """Get today's total cash box"""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    total = db.query(func.sum(Payment.montant)).filter(
        and_(
            Payment.created_at >= today_start,
            Payment.created_at <= today_end
        )
    ).scalar()

    return total or Decimal("0")

