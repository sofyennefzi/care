from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, Enum, DECIMAL, ForeignKey, Text, JSON, text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    staff = "staff"


class AppointmentState(str, enum.Enum):
    en_attente = "en_attente"
    valide = "valide"
    annule = "annule"


class PaymentMode(str, enum.Enum):
    espece = "espece"
    carte = "carte"
    virement = "virement"
    cheque = "cheque"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.staff)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    audit_logs = relationship("AuditLog", back_populates="user")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    date_naissance = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    requires_validation = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    appointments = relationship("Appointment", back_populates="patient")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    prix_base = Column(DECIMAL(12, 2), nullable=False)
    actif = Column(Boolean, default=True, nullable=False)

    appointments = relationship("Appointment", back_populates="service")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    heure = Column(Time, nullable=False)
    prix = Column(DECIMAL(12, 2), nullable=False)
    verse = Column(DECIMAL(12, 2), default=0, nullable=False)
    reste = Column(DECIMAL(12, 2), nullable=False, server_default=text("0"))
    etat = Column(Enum(AppointmentState), default=AppointmentState.en_attente, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    patient = relationship("Patient", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")
    payments = relationship("Payment", back_populates="appointment")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    montant = Column(DECIMAL(12, 2), nullable=False)
    mode = Column(Enum(PaymentMode), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    appointment = relationship("Appointment", back_populates="payments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    target_table = Column(String(100), nullable=False)
    target_id = Column(Integer, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="audit_logs")
