from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta
from typing import Optional, List
from decimal import Decimal

import uvicorn
from database import get_db, engine
from models import Base, AppointmentState, PaymentMode, UserRole
import schemas
import crud
import auth
from stats import get_dashboard_stats

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinic Management System")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Template filters
def format_date(value):
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return value

def format_time(value):
    if isinstance(value, time):
        return value.strftime("%H:%M")
    return value

def format_currency(value):
    if value is None:
        return "0 DA"
    return f"{float(value):,.2f} DA"

templates.env.filters["format_date"] = format_date
templates.env.filters["format_time"] = format_time
templates.env.filters["format_currency"] = format_currency


# ============ Authentication Routes ============

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Nom d'utilisateur ou mot de passe incorrect"},
            status_code=400
        )

    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response


# ============ Dashboard ============

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    stats = get_dashboard_stats(db)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": current_user, "stats": stats}
    )


# ============ Clients (Patients) ============

@app.get("/clients", response_class=HTMLResponse)
async def clients_page(
    request: Request,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    patients = crud.get_patients(db, search=search)
    return templates.TemplateResponse(
        "clients.html",
        {"request": request, "user": current_user, "patients": patients, "search": search or ""}
    )


# ============ RDV Aujourd'hui ============

@app.get("/today", response_class=HTMLResponse)
async def today_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    appointments = crud.get_today_appointments(db)
    return templates.TemplateResponse(
        "today.html",
        {"request": request, "user": current_user, "appointments": appointments}
    )


# ============ Rendez-vous ============

@app.get("/rdv", response_class=HTMLResponse)
async def rdv_page(
    request: Request,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    appointments = crud.get_appointments(db, search=search)
    patients = crud.get_patients(db, limit=1000)
    services = crud.get_services(db)
    return templates.TemplateResponse(
        "rdv.html",
        {
            "request": request,
            "user": current_user,
            "appointments": appointments,
            "patients": patients,
            "services": services,
            "search": search or ""
        }
    )


# ============ Agenda ============

@app.get("/agenda", response_class=HTMLResponse)
async def agenda_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    return templates.TemplateResponse(
        "agenda.html",
        {"request": request, "user": current_user}
    )


# ============ Valider Clients ============

@app.get("/clients/valider", response_class=HTMLResponse)
async def valider_clients_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    patients = crud.get_patients_requiring_validation(db)
    return templates.TemplateResponse(
        "valider_clients.html",
        {"request": request, "user": current_user, "patients": patients}
    )


# ============ En Attente ============

@app.get("/rdv/en-attente", response_class=HTMLResponse)
async def en_attente_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    appointments = crud.get_appointments(db, etat=AppointmentState.en_attente)
    return templates.TemplateResponse(
        "en_attente.html",
        {"request": request, "user": current_user, "appointments": appointments}
    )


# ============ Paiements ============

@app.get("/paiements", response_class=HTMLResponse)
async def paiements_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    # Get all appointments with outstanding balances or payments
    appointments = crud.get_appointments(db, limit=1000)
    caisse_jour = crud.get_caisse_du_jour(db)

    return templates.TemplateResponse(
        "paiements.html",
        {
            "request": request,
            "user": current_user,
            "appointments": appointments,
            "caisse_jour": caisse_jour
        }
    )


# ============ API Routes ============

# Stats API
@app.get("/api/stats/overview")
async def api_stats_overview(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    stats = get_dashboard_stats(db, date_from, date_to)
    return stats


# Patient API
@app.get("/api/patients", response_model=List[schemas.PatientResponse])
async def api_get_patients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    patients = crud.get_patients(db, skip=skip, limit=limit, search=search)
    return patients


@app.post("/api/patients", response_model=schemas.PatientResponse)
async def api_create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    return crud.create_patient(db, patient, current_user.id)


@app.get("/api/patients/{patient_id}", response_model=schemas.PatientResponse)
async def api_get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return patient


@app.patch("/api/patients/{patient_id}", response_model=schemas.PatientResponse)
async def api_update_patient(
    patient_id: int,
    patient: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    updated_patient = crud.update_patient(db, patient_id, patient, current_user.id)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return updated_patient


@app.delete("/api/patients/{patient_id}")
async def api_delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_admin)
):
    success = crud.delete_patient(db, patient_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return {"message": "Patient supprimé"}


# Service API
@app.get("/api/services", response_model=List[schemas.ServiceResponse])
async def api_get_services(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    return crud.get_services(db)


# Appointment API
@app.get("/api/rdv", response_model=List[schemas.AppointmentResponse])
async def api_get_appointments(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    etat: Optional[AppointmentState] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    patient_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    appointments = crud.get_appointments(
        db, skip=skip, limit=limit, search=search,
        etat=etat, date_from=date_from, date_to=date_to, patient_id=patient_id
    )
    return appointments


@app.post("/api/rdv", response_model=schemas.AppointmentResponse)
async def api_create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    try:
        return crud.create_appointment(db, appointment, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/rdv/{appointment_id}", response_model=schemas.AppointmentResponse)
async def api_get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    appointment = crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
    return appointment


@app.patch("/api/rdv/{appointment_id}", response_model=schemas.AppointmentResponse)
async def api_update_appointment(
    appointment_id: int,
    appointment: schemas.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    try:
        updated = crud.update_appointment(db, appointment_id, appointment, current_user.id)
        if not updated:
            raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/rdv/{appointment_id}")
async def api_delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_admin)
):
    success = crud.delete_appointment(db, appointment_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Rendez-vous introuvable")
    return {"message": "Rendez-vous supprimé"}


# Payment API
@app.get("/api/rdv/{appointment_id}/payments", response_model=List[schemas.PaymentResponse])
async def api_get_payments(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    return crud.get_payments_for_appointment(db, appointment_id)


@app.post("/api/rdv/{appointment_id}/payments", response_model=schemas.PaymentResponse)
async def api_create_payment(
    appointment_id: int,
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    if payment.appointment_id != appointment_id:
        raise HTTPException(status_code=400, detail="ID de rendez-vous non concordant")
    try:
        return crud.create_payment(db, payment, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Agenda API (FullCalendar format)
@app.get("/api/agenda")
async def api_agenda(
    start: str,
    end: str,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.require_login)
):
    start_date = datetime.fromisoformat(start.replace('Z', '+00:00')).date()
    end_date = datetime.fromisoformat(end.replace('Z', '+00:00')).date()

    appointments = crud.get_appointments(db, date_from=start_date, date_to=end_date, limit=1000)

    events = []
    for appt in appointments:
        # Combine date and time for start
        start_datetime = datetime.combine(appt.date, appt.heure)
        # Assume 30min duration
        end_datetime = start_datetime + timedelta(minutes=30)

        # Color based on state
        color_map = {
            "en_attente": "#ffc107",  # warning/yellow
            "valide": "#28a745",      # success/green
            "annule": "#dc3545"       # danger/red
        }

        events.append({
            "id": appt.id,
            "title": f"{appt.patient.prenom} {appt.patient.nom} - {appt.service.nom}",
            "start": start_datetime.isoformat(),
            "end": end_datetime.isoformat(),
            "backgroundColor": color_map.get(appt.etat.value, "#6c757d"),
            "borderColor": color_map.get(appt.etat.value, "#6c757d"),
            "extendedProps": {
                "patientId": appt.patient_id,
                "patientName": f"{appt.patient.prenom} {appt.patient.nom}",
                "serviceName": appt.service.nom,
                "etat": appt.etat.value,
                "prix": float(appt.prix),
                "verse": float(appt.verse),
                "reste": float(appt.reste)
            }
        })

    return events


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
pymysql==1.1.0
cryptography==42.0.0
python-multipart==0.0.6
jinja2==3.1.3
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-dateutil==2.8.2
pydantic==2.5.3
pydantic-settings==2.1.0

