# ...existing code...
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/add/', views.client_add, name='client_add'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/<int:pk>/edit/', views.client_edit, name='client_edit'),
    path('rdv/', views.rdv_list, name='rdv_list'),
    path('rdv/add/', views.rdv_add, name='rdv_add'),
    path('rdv/<int:pk>/', views.rdv_detail, name='rdv_detail'),
    path('rdv/<int:pk>/edit/', views.rdv_edit, name='rdv_edit'),
    path('agenda/', views.agenda, name='agenda'),
    path('paiements/', views.paiements_list, name='paiements_list'),
    path('paiements/add/', views.paiement_add, name='paiement_add'),
]

