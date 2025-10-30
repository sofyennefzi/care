# 🏥 Système de Gestion de Clinique

Application web complète de gestion de rendez-vous pour cliniques dentaires/médicales en Tunisie.

## 📋 Fonctionnalités

### ✅ Gestion complète
- **Dashboard** - Statistiques en temps réel, graphiques, revenus
- **Clients** - CRUD complet, recherche, validation
- **Rendez-vous** - Création, modification, annulation, états
- **Agenda** - Calendrier interactif FullCalendar avec drag & drop
- **Paiements** - Suivi des paiements, caisse du jour, historique
- **En Attente** - Vue filtrée des RDV en attente
- **Validation Clients** - Workflow d'approbation des nouveaux clients

### 🔐 Sécurité
- Authentification JWT avec cookies HTTP-only
- Rôles: Admin et Staff
- Hachage des mots de passe avec bcrypt
- Protection CSRF
- Audit log de toutes les modifications

### 💰 Gestion financière
- Monnaie: **Dinar Tunisien (TND)**
- Calcul automatique du reste à payer
- Historique complet des paiements
- Modes: Espèce, Carte, Virement, Chèque
- Caisse du jour en temps réel

## 🚀 Installation

### Prérequis
- Python 3.12+
- MySQL 8.0+
- Git

### Étapes

1. **Cloner le projet**
```bash
git clone <url>
cd care
```

2. **Créer l'environnement virtuel**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Créer la base de données MySQL**
```sql
CREATE DATABASE clinic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. **Configurer l'environnement**
Le fichier `.env` est déjà configuré:
```env
DATABASE_URL=mysql+pymysql://root:@localhost:3306/clinic_db
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

6. **Peupler la base de données** (optionnel mais recommandé)
```bash
python quick_seed.py
```

Cela crée:
- 2 utilisateurs (admin/admin123, staff1/staff123)
- 5 services
- 5 patients
- 5 rendez-vous de test

7. **Démarrer l'application**
```bash
python main.py
```

8. **Ouvrir dans le navigateur**
```
http://localhost:8000
```

## 📱 Utilisation

### Connexion
- **Admin**: `admin` / `admin123`
- **Staff**: `staff1` / `staff123`

### Navigation
Toutes les pages sont accessibles via la sidebar gauche:
- Dashboard
- Clients
- RDV Aujourd'hui
- Rendez-vous
- Agenda
- Valider Clients
- En Attente
- Paiements
- Déconnexion

### Guide de l'Agenda
Voir [GUIDE_AGENDA.md](GUIDE_AGENDA.md) pour un guide complet d'utilisation de l'agenda.

## 🛠️ Stack Technique

### Backend
- **FastAPI** 0.115.0 - Framework web moderne
- **SQLAlchemy** 2.0.32 - ORM
- **Alembic** - Migrations de base de données
- **PyMySQL** 1.1.1 - Connecteur MySQL
- **Pydantic** - Validation des données
- **python-jose** - JWT
- **passlib** - Hachage bcrypt

### Frontend
- **Bootstrap 5** - UI framework
- **Bootstrap Icons** - Icônes
- **Chart.js** 4.4.0 - Graphiques
- **FullCalendar** 6.1.9 - Calendrier interactif
- **Jinja2** - Templates

### Base de données
- **MySQL** 8.0+
- Schéma normalisé
- Contraintes d'intégrité référentielle
- Index pour les performances

## 📊 Structure de la base de données

### Tables principales
- **users** - Utilisateurs du système
- **patients** - Clients/Patients
- **services** - Services médicaux offerts
- **appointments** - Rendez-vous
- **payments** - Paiements
- **audit_logs** - Historique des modifications

### Relations
```
User (1) ----< (N) AuditLog
Patient (1) ----< (N) Appointment
Service (1) ----< (N) Appointment
Appointment (1) ----< (N) Payment
```

## 🔧 Configuration

### Fichiers importants
- `.env` - Variables d'environnement
- `alembic.ini` - Configuration des migrations
- `requirements.txt` - Dépendances Python
- `main.py` - Point d'entrée de l'application

### Variables d'environnement
- `DATABASE_URL` - URL de connexion MySQL
- `SECRET_KEY` - Clé secrète pour JWT
- `ALGORITHM` - Algorithme JWT (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Durée de session

## 📈 API REST

### Endpoints principaux

#### Authentification
- `POST /login` - Connexion
- `GET /logout` - Déconnexion

#### Patients
- `GET /api/patients` - Liste
- `POST /api/patients` - Créer
- `GET /api/patients/{id}` - Détails
- `PATCH /api/patients/{id}` - Modifier
- `DELETE /api/patients/{id}` - Supprimer (admin)

#### Rendez-vous
- `GET /api/rdv` - Liste (avec filtres)
- `POST /api/rdv` - Créer
- `GET /api/rdv/{id}` - Détails
- `PATCH /api/rdv/{id}` - Modifier
- `DELETE /api/rdv/{id}` - Supprimer (admin)

#### Paiements
- `GET /api/rdv/{id}/payments` - Liste des paiements
- `POST /api/rdv/{id}/payments` - Ajouter paiement

#### Agenda
- `GET /api/agenda?start={date}&end={date}` - Événements (format FullCalendar)

#### Statistiques
- `GET /api/stats/overview?from={date}&to={date}` - Stats dashboard

## 🧪 Tests

```bash
# Test simple des endpoints
python tests/test_agenda.py
python tests/smoke_clients.py
```

## 📝 Règles métier

1. **Calcul automatique**: `reste = prix - versé`
2. **Pas de chevauchement**: Un patient ne peut avoir 2 RDV à la même date/heure
3. **États des RDV**:
   - `en_attente` → `valide` ou `annule`
   - `valide` → `annule`
   - `annule` = terminal (pas de paiements)
4. **Caisse du jour**: Somme des paiements de la journée en cours
5. **Audit**: Toutes les modifications sont tracées

## 🎨 Personnalisation

### Changer la devise
Modifier `format_currency` dans `main.py`:
```python
def format_currency(value):
    if value is None:
        return "0 TND"
    return f"{float(value):,.2f} TND"
```

### Ajouter un nouveau service
Via l'interface admin ou directement en base:
```sql
INSERT INTO services (nom, description, prix_base, actif) 
VALUES ('Détartrage', 'Nettoyage dentaire', 80.00, 1);
```

## 🐛 Dépannage

### Erreur de connexion MySQL
```
Access denied for user 'root'@'localhost'
```
→ Vérifiez le mot de passe dans `.env` et les permissions MySQL

### Port 8000 déjà utilisé
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill <PID>
```

### Templates Jinja errors
→ Assurez-vous que tous les blocs `{% block %}` sont fermés avec `{% endblock %}`

### Browser extensions causing CORS errors
→ Utilisez une fenêtre de navigation privée ou désactivez les extensions pour localhost

## 📞 Support

Pour toute question ou problème:
1. Vérifiez les logs dans la console serveur
2. Consultez `GUIDE_AGENDA.md` pour l'agenda
3. Vérifiez les erreurs dans la console du navigateur (F12)

## 📄 Licence

Ce projet est privé et confidentiel.

## 👥 Auteurs

Développé pour la gestion de cliniques dentaires en Tunisie.

---

**Version**: 1.0.0  
**Date**: Octobre 2025  
**Langue**: Français  
**Devise**: Dinar Tunisien (TND)

