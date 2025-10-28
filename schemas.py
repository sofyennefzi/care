from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime, date, time
from decimal import Decimal
from models import UserRole, AppointmentState, PaymentMode


# User schemas
class UserBase(BaseModel):
    username: str
    role: UserRole = UserRole.staff
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Patient schemas
class PatientBase(BaseModel):
    nom: str
    prenom: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    date_naissance: Optional[date] = None
    notes: Optional[str] = None
    requires_validation: bool = False


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    date_naissance: Optional[date] = None
    notes: Optional[str] = None
    requires_validation: Optional[bool] = None


class PatientResponse(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Service schemas
class ServiceBase(BaseModel):
    nom: str
    description: Optional[str] = None
    prix_base: Decimal
    actif: bool = True


class ServiceResponse(ServiceBase):
    id: int

    class Config:
        from_attributes = True


# Appointment schemas
class AppointmentBase(BaseModel):
    patient_id: int
    service_id: int
    date: date
    heure: time
    prix: Decimal
    verse: Decimal = Decimal("0")
    etat: AppointmentState = AppointmentState.en_attente
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    patient_id: Optional[int] = None
    service_id: Optional[int] = None
    date: Optional[date] = None
    heure: Optional[time] = None
    prix: Optional[Decimal] = None
    verse: Optional[Decimal] = None
    etat: Optional[AppointmentState] = None
    notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    id: int
    reste: Decimal
    created_at: datetime
    patient: PatientResponse
    service: ServiceResponse

    class Config:
        from_attributes = True


# Payment schemas
class PaymentBase(BaseModel):
    appointment_id: int
    montant: Decimal
    mode: PaymentMode


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Stats schemas
class StatsOverview(BaseModel):
    total_patients: int
    total_rdv: int
    rdv_passes: int
    rdv_futurs: int
    revenu_total: Decimal
    caisse_jour: Decimal
    repartition_etat: dict
    rdv_par_jour: dict
    top_services: list


# Login schema
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

