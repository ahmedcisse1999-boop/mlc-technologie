# stock/admin.py
from django.contrib import admin
from .models import Produit, Categorie, Fournisseur, Client, Facture, Devis, MouvementStock, Paiement
from .models import Profil
admin.site.register(Profil)

admin.site.register(Produit)
admin.site.register(Categorie)
admin.site.register(Fournisseur)
admin.site.register(Client)
admin.site.register(Facture)
admin.site.register(Devis)
admin.site.register(MouvementStock)
admin.site.register(Paiement)