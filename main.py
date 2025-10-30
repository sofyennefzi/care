from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta
from typing import Optional, List
from decimal import Decimal
from contextlib import asynccontextmanager
import json

import uvicorn
from database import get_db, engine
from models import Base, AppointmentState, PaymentMode, UserRole
import schemas
import crud
import auth
from stats import get_dashboard_stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("Starting up application...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not create database tables: {e}")
        print("Make sure MySQL is running and database 'clinic_db' exists")
        print("Check your .env file for correct database credentials")

    yield

    # Shutdown
    print("Shutting down application...")


app = FastAPI(title="Clinic Management System", lifespan=lifespan)

# Exception handler for authentication errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # If it's a 401 error and the request is for an HTML page, redirect to login
    if exc.status_code == 401:
        # Check if the request accepts HTML (browser request)
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    # For API requests or other errors, return JSON
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

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
        return "0 TND"
    return f"{float(value):,.2f} TND"

templates.env.filters["format_date"] = format_date
templates.env.filters["format_time"] = format_time
templates.env.filters["format_currency"] = format_currency
templates.env.filters["tojson"] = lambda v: json.dumps(v, ensure_ascii=False)


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
async def root(request: Request, db: Session = Depends(get_db)):
    # Check if user is logged in
    user = auth.get_current_user_from_cookie(request, db)
    if user:
        return RedirectResponse(url="/dashboard")
    else:
        return RedirectResponse(url="/login")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
):
    patients = crud.get_patients(db, search=search)
    try:
        return templates.TemplateResponse(
            "clients.html",
            {"request": request, "user": current_user, "patients": patients, "search": search or ""}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Fallback: show a minimal HTML error to identify the root cause quickly
        return HTMLResponse(
            content=f"<h3>Erreur d'affichage /clients</h3><pre>{str(e)}</pre>",
            status_code=500
        )


# ============ RDV Aujourd'hui ============

@app.get("/today", response_class=HTMLResponse)
async def today_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
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


# ============ Services ============

@app.get("/test-services-direct", response_class=HTMLResponse)
async def test_services_direct(request: Request):
    """Direct test page for services API - no auth required for debugging"""
    return templates.TemplateResponse("test_services_direct.html", {"request": request})


@app.get("/services", response_class=HTMLResponse)
async def services_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
):
    services = crud.get_services(db, active_only=False)
    return templates.TemplateResponse(
        "services.html",
        {"request": request, "user": current_user, "services": services}
    )


# ============ API Routes ============

# Stats API
@app.get("/api/stats/overview")
async def api_stats_overview(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
):
    patients = crud.get_patients(db, skip=skip, limit=limit, search=search)
    return patients


@app.post("/api/patients", response_model=schemas.PatientResponse)
async def api_create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
):
    return crud.create_patient(db, patient, current_user.id)


@app.get("/api/patients/{patient_id}", response_model=schemas.PatientResponse)
async def api_get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
):
    updated_patient = crud.update_patient(db, patient_id, patient, current_user.id)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return updated_patient


@app.delete("/api/patients/{patient_id}")
async def api_delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_admin)
):
    success = crud.delete_patient(db, patient_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return {"message": "Patient supprimé"}


# Service API
@app.get("/api/services", response_model=List[schemas.ServiceResponse])
async def api_get_services(
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
):
    try:
        print(f"[DEBUG] Getting services for user: {current_user.username}")
        services = crud.get_services(db, active_only=True)
        print(f"[DEBUG] Found {len(services)} services")
        return services
    except Exception as e:
        print(f"[ERROR] Failed to get services: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@app.get("/api/services/{service_id}", response_model=schemas.ServiceResponse)
async def api_get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
):
    service = crud.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service introuvable")
    return service


@app.post("/api/services", response_model=schemas.ServiceResponse)
async def api_create_service(
    service: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
):
    return crud.create_service(db, service, current_user.id)


@app.patch("/api/services/{service_id}", response_model=schemas.ServiceResponse)
async def api_update_service(
    service_id: int,
    service: schemas.ServiceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
):
    updated_service = crud.update_service(db, service_id, service, current_user.id)
    if not updated_service:
        raise HTTPException(status_code=404, detail="Service introuvable")
    return updated_service


@app.delete("/api/services/{service_id}")
async def api_delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_admin)
):
    success = crud.delete_service(db, service_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Service introuvable")
    return {"message": "Service supprimé"}


    success = crud.delete_patient(db, patient_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return {"message": "Patient supprimé"}



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
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
):
    try:
        return crud.create_appointment(db, appointment, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/rdv/{appointment_id}", response_model=schemas.AppointmentResponse)
async def api_get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_admin)
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
    current_user = Depends(auth.require_login)
):
    return crud.get_payments_for_appointment(db, appointment_id)


@app.post("/api/rdv/{appointment_id}/payments", response_model=schemas.PaymentResponse)
async def api_create_payment(
    appointment_id: int,
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.require_login)
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
    current_user = Depends(auth.require_login)
):
    try:
        # More flexible date parsing
        # Remove 'Z' and handle various formats
        start_clean = start.replace('Z', '').replace('+00:00', '')
        end_clean = end.replace('Z', '').replace('+00:00', '')

        # Try to parse with time, if that fails, just use the date part
        try:
            start_date = datetime.fromisoformat(start_clean).date()
        except ValueError:
            # If full datetime parsing fails, try just the date part
            start_date = datetime.strptime(start_clean.split('T')[0], '%Y-%m-%d').date()

        try:
            end_date = datetime.fromisoformat(end_clean).date()
        except ValueError:
            end_date = datetime.strptime(end_clean.split('T')[0], '%Y-%m-%d').date()

        print(f"[API AGENDA] Loading appointments from {start_date} to {end_date}")

        appointments = crud.get_appointments(db, date_from=start_date, date_to=end_date, limit=1000)

        print(f"[API AGENDA] Found {len(appointments)} appointments")

        events = []
        for appt in appointments:
            try:
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
            except Exception as e:
                print(f"[API AGENDA] Error processing appointment {appt.id}: {e}")
                continue

        print(f"[API AGENDA] Returning {len(events)} events")
        return events

    except Exception as e:
        print(f"[API AGENDA] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement des rendez-vous: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
