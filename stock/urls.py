from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'stock'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Produits
    path('produits/', views.produit_liste, name='produit_liste'),
    path('produits/ajouter/', views.produit_ajouter, name='produit_ajouter'),
    path('produits/<int:pk>/modifier/', views.produit_modifier, name='produit_modifier'),
    path('produits/<int:pk>/supprimer/', views.produit_supprimer, name='produit_supprimer'),

    # Catégories
    path('categories/', views.categorie_liste, name='categorie_liste'),
    path('categories/ajouter/', views.categorie_ajouter, name='categorie_ajouter'),

    # Fournisseurs
    path('fournisseurs/', views.fournisseur_liste, name='fournisseur_liste'),
    path('fournisseurs/ajouter/', views.fournisseur_ajouter, name='fournisseur_ajouter'),
    path('fournisseurs/<int:pk>/modifier/', views.fournisseur_modifier, name='fournisseur_modifier'),
    path('fournisseurs/<int:pk>/supprimer/', views.fournisseur_supprimer, name='fournisseur_supprimer'),

    # Clients
    path('clients/', views.client_liste, name='client_liste'),
    path('clients/ajouter/', views.client_ajouter, name='client_ajouter'),
    path('clients/<int:pk>/modifier/', views.client_modifier, name='client_modifier'),
    path('clients/<int:pk>/supprimer/', views.client_supprimer, name='client_supprimer'),

    # Mouvements de stock
    path('mouvements/', views.mouvement_liste, name='mouvement_liste'),
    path('mouvements/ajouter/', views.mouvement_ajouter, name='mouvement_ajouter'),

    # Alertes
    path('alertes/', views.alertes, name='alertes'),

    # Devis
    path('devis/', views.devis_liste, name='devis_liste'),
    path('devis/ajouter/', views.devis_ajouter, name='devis_ajouter'),
    path('devis/<int:pk>/', views.devis_detail, name='devis_detail'),

    # Factures
    path('factures/', views.facture_liste, name='facture_liste'),
    path('factures/ajouter/', views.facture_ajouter, name='facture_ajouter'),
    path('factures/<int:pk>/', views.facture_detail, name='facture_detail'),
    path('factures/<int:pk>/pdf/', views.facture_pdf, name='facture_pdf'),

    # Rapports
    path('rapports/', views.rapports, name='rapports'),
    
    # Ajoute ces lignes dans urlpatterns
    path('factures/<int:pk>/supprimer/', views.facture_supprimer, name='facture_supprimer'),
    path('factures/<int:pk>/pdf/', views.facture_pdf, name='facture_pdf'),
    path('devis/<int:pk>/pdf/', views.devis_pdf, name='devis_pdf'),
    
    
    
    path('fournisseurs/quick-add/', views.fournisseur_form, name='fournisseur_quick'),
    path('clients/quick-add/', views.client_form, name='client_quick'),
    path('categories/quick-add/', views.categorie_form, name='categorie_quick'),
    
    
    
    
    # Factures avancées
   path('factures/<int:pk>/modifier/', views.facture_modifier, name='facture_modifier'),
   path('factures/<int:pk>/paiement/', views.paiement_ajouter, name='paiement_ajouter'),
   path('paiements/', views.paiement_liste, name='paiement_liste'),

# Devis avancé
   path('devis/<int:pk>/modifier/', views.devis_modifier, name='devis_modifier'),
   path('devis/<int:pk>/supprimer/', views.devis_supprimer, name='devis_supprimer'),

# API lignes (AJAX)
   path('api/produit/<int:pk>/', views.api_produit_prix, name='api_produit_prix'),
   path('categories/<int:pk>/supprimer/', views.categorie_supprimer, name='categorie_supprimer'),
   path('ventes/', views.vente_liste, name='vente_liste'),
   path('devis/<int:pk>/accepter/', views.devis_accepter, name='devis_accepter'),
   
   

# Ajoute ces URLs
  path('login/',   views.login_view,  name='login'),
  path('logout/',  views.logout_view, name='logout'),
  path('profil/',  views.profil_view, name='profil'),
  
  
  
  # TERRAIN
path('installations/',                    views.installation_liste,   name='installation_liste'),
path('installations/ajouter/',            views.installation_ajouter, name='installation_ajouter'),
path('installations/<int:pk>/',           views.installation_detail,  name='installation_detail'),
path('installations/<int:pk>/modifier/',  views.installation_modifier, name='installation_modifier'),
path('installations/<int:pk>/supprimer/', views.installation_supprimer, name='installation_supprimer'),

path('maintenances/',                    views.maintenance_liste,   name='maintenance_liste'),
path('maintenances/ajouter/',            views.maintenance_ajouter, name='maintenance_ajouter'),
path('maintenances/<int:pk>/',           views.maintenance_detail,  name='maintenance_detail'),
path('maintenances/<int:pk>/modifier/',  views.maintenance_modifier, name='maintenance_modifier'),
path('maintenances/<int:pk>/supprimer/', views.maintenance_supprimer, name='maintenance_supprimer'),

path('contrats/',                    views.contrat_liste,   name='contrat_liste'),
path('contrats/ajouter/',            views.contrat_ajouter, name='contrat_ajouter'),
path('contrats/<int:pk>/',           views.contrat_detail,  name='contrat_detail'),
path('contrats/<int:pk>/modifier/',  views.contrat_modifier, name='contrat_modifier'),
path('contrats/<int:pk>/supprimer/', views.contrat_supprimer, name='contrat_supprimer'),

path('sites/',                    views.site_liste,   name='site_liste'),
path('sites/ajouter/',            views.site_ajouter, name='site_ajouter'),
path('sites/<int:pk>/supprimer/', views.site_supprimer, name='site_supprimer'),



path('installations/quick-add/', views.installation_quick, name='installation_quick'),


path('produits/<int:pk>/', views.produit_detail, name='produit_detail'),
path('categories/quick-add/', views.categorie_form, name='categorie_quick'),
path('fournisseurs/quick-add/', views.fournisseur_form, name='fournisseur_quick'),


path('mouvements/<int:pk>/',           views.mouvement_detail,   name='mouvement_detail'),
path('mouvements/<int:pk>/modifier/',  views.mouvement_modifier,  name='mouvement_modifier'),
path('mouvements/<int:pk>/supprimer/', views.mouvement_supprimer, name='mouvement_supprimer'),

path('clients/<int:pk>/', views.client_detail, name='client_detail'),  

path('categories/<int:pk>/',          views.categorie_detail,   name='categorie_detail'),
path('categories/<int:pk>/modifier/', views.categorie_modifier,  name='categorie_modifier'),
path('fournisseurs/<int:pk>/', views.fournisseur_detail, name='fournisseur_detail'),


path('sites/<int:pk>/',          views.site_detail,  name='site_detail'),
path('sites/<int:pk>/modifier/', views.site_modifier, name='site_modifier'),

path('sites/quick-add/', views.site_quick, name='site_quick'),
  
   
]# T