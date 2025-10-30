# 📅 Guide d'utilisation de l'Agenda

## ✅ Fonctionnalités disponibles

### 1. **Créer un rendez-vous**
   - **Méthode 1**: Cliquez sur le bouton **"+ Ajouter RDV"** en haut à droite
   - **Méthode 2**: Cliquez directement sur une date dans le calendrier
   - Remplissez le formulaire:
     - Client (requis)
     - Service (requis) - le prix se remplit automatiquement
     - Date & Heure (requis)
     - Prix (requis)
     - Versé (optionnel, par défaut 0)
     - État (En attente ou Validé)
     - Notes (optionnel)
   - Cliquez sur **"Enregistrer"**
   - Le calendrier se rafraîchit automatiquement

### 2. **Voir les détails d'un rendez-vous**
   - Cliquez sur n'importe quel événement dans le calendrier
   - Une fenêtre modale s'ouvre avec:
     - Nom du patient
     - Service
     - Date et heure
     - État (badge coloré)
     - Prix, Versé, Reste (en TND)

### 3. **Modifier un rendez-vous**
   - **Méthode 1**: Cliquez sur l'événement → bouton **"Modifier"**
   - **Méthode 2**: Glissez-déposez l'événement sur une autre date (drag & drop)
   - Dans le formulaire de modification, vous pouvez changer:
     - Date
     - Heure
     - Prix
     - État (En attente, Validé, Annulé)
     - Notes
   - Le patient et le service ne peuvent pas être modifiés (créer un nouveau RDV si nécessaire)
   - Cliquez sur **"Mettre à jour"**

### 4. **Supprimer un rendez-vous**
   - Cliquez sur l'événement
   - Cliquez sur le bouton rouge **"Supprimer"**
   - Confirmez la suppression
   - L'événement disparaît immédiatement du calendrier

### 5. **Déplacer un rendez-vous (Drag & Drop)**
   - Cliquez et maintenez sur un événement
   - Faites-le glisser vers une autre date
   - Relâchez
   - L'heure reste la même, seule la date change
   - Un message de confirmation apparaît
   - Si le patient a déjà un RDV à cette date/heure, vous aurez un message d'erreur

## 🎨 Codes couleurs des événements

- 🟡 **Jaune** = En attente
- 🟢 **Vert** = Validé
- 🔴 **Rouge** = Annulé

## 🔄 Vues disponibles

- **Mois** (par défaut) - Vue mensuelle complète
- **Semaine** - Vue hebdomadaire détaillée avec heures
- **Jour** - Vue journalière avec créneaux horaires

Utilisez les boutons en haut à droite pour basculer entre les vues.

## 🔔 Notifications

Après chaque action, un message toast apparaît pour confirmer:
- ✅ "Rendez-vous ajouté avec succès"
- ✅ "Rendez-vous modifié avec succès"
- ✅ "Rendez-vous déplacé avec succès"
- ✅ "Rendez-vous supprimé"
- ❌ Messages d'erreur en cas de problème

## 💡 Astuces

1. **Double-vérification**: Avant de supprimer, vérifiez les paiements dans la page Paiements
2. **Recherche rapide**: Utilisez Ctrl+F dans le calendrier pour trouver un patient
3. **Navigation rapide**: 
   - Bouton "Aujourd'hui" pour revenir à la date du jour
   - Flèches ← → pour naviguer entre mois/semaines/jours
4. **Planning efficace**: La vue Semaine est idéale pour organiser les RDV quotidiens

## 🔗 Intégration avec les autres pages

- Les RDV créés dans l'Agenda apparaissent automatiquement dans **Rendez-vous**
- Les paiements se gèrent dans la page **Paiements**
- Les clients se créent dans la page **Clients**
- Le dashboard affiche les statistiques de tous les RDV

## ⚙️ Règles automatiques

- Le reste à payer = Prix - Versé (calculé automatiquement)
- Impossible de créer deux RDV pour le même patient à la même date/heure
- Impossible d'ajouter des paiements à un RDV annulé
- Les événements annulés restent visibles mais en rouge

---

**Besoin d'aide ?** Consultez les autres pages pour:
- Gérer les clients → `/clients`
- Voir tous les RDV → `/rdv`
- Gérer les paiements → `/paiements`

