# ✅ Services Management - Complete Guide

## What was added

### 1. **New Services Page** (`/services`)
A full CRUD interface to manage services that appear in the agenda and RDV forms.

**Features:**
- ✅ View all services in a table
- ✅ Add new services with modal form
- ✅ Edit existing services (name, description, price, status)
- ✅ Activate/Deactivate services
- ✅ All prices in TND

**How to access:**
- Click **"Services"** in the left sidebar (under Paiements)
- Or navigate to: `http://localhost:8000/services`

### 2. **Services API Endpoints**

All fully functional:

```
GET    /api/services              - List all active services
GET    /api/services/{id}          - Get one service
POST   /api/services              - Create service
PATCH  /api/services/{id}          - Update service  
DELETE /api/services/{id}          - Delete service (admin only)
```

### 3. **Integration with Agenda**

Services automatically load in the "Ajouter RDV" modal:
- Dropdown shows: `Service Name - Price TND`
- When you select a service, the price auto-fills
- All active services appear in the list

## How to use Services in the Agenda

### Step 1: Add Services (if needed)
1. Go to `/services` page
2. Click **"+ Ajouter Service"**
3. Fill in:
   - Nom (required) - e.g., "Détartrage"
   - Description - e.g., "Nettoyage dentaire professionnel"
   - Prix de base (TND) - e.g., 80.00
   - Service actif ✓
4. Click **"Enregistrer"**

### Step 2: Use in Agenda
1. Go to `/agenda`
2. Click **"+ Ajouter RDV"** or click on a date
3. Select a **Client** from dropdown
4. Select a **Service** from dropdown ← **Services appear here!**
5. The **Prix** field auto-fills with the service price
6. Fill in Date, Heure, etc.
7. Click **"Enregistrer"**

## Troubleshooting

### "No services in dropdown"

**Check 1: Are services active?**
- Go to `/services`
- Make sure services have green "Actif" badge
- If a service is "Inactif", click "Activer"

**Check 2: Browser console**
1. Open agenda: `http://localhost:8000/agenda`
2. Press F12 to open DevTools
3. Go to **Console** tab
4. Look for:
   ```
   Loaded services: [Array of services]
   Added X services to dropdown
   ```
5. If you see errors, share them

**Check 3: Test API directly**
Open in browser: `http://localhost:8000/api/services`
Should return JSON array of services.

**Quick Fix:**
1. Make sure server is running: `python main.py`
2. Hard refresh the agenda page: `Ctrl+F5`
3. Check that at least one service exists in `/services`

## Current Services (from seed)

Your database should have these 5 services:
1. Consultation - 50.00 TND
2. Détartrage - 80.00 TND
3. Plombage - 120.00 TND
4. Couronne - 400.00 TND
5. Implant - 1500.00 TND

Plus any you added (like "Radiographie" from the test).

## Testing

To verify everything works:

```bash
# Run the test script
python tests\test_services.py
```

Expected output:
```
POST /login 302 /dashboard
GET /services 200 OK
GET /api/services 200
  Found 6 services
  Sample: Consultation - 50.00 TND
```

## Summary

✅ Services page created
✅ Full CRUD API working
✅ Agenda loads services automatically
✅ RDV page also uses services
✅ All prices in TND
✅ Active/Inactive toggle

**Next steps for you:**
1. Restart server: `python main.py`
2. Go to http://localhost:8000/services
3. Verify services exist
4. Go to http://localhost:8000/agenda
5. Click "+ Ajouter RDV"
6. Check the "Service" dropdown - should have all active services!

If still not working, open browser console (F12) and check for errors.

