# stock/forms.py

from django import forms
from .models import Paiement, Produit, Fournisseur, Client, MouvementStock, Devis, LigneDevis, Facture, LigneFacture, Categorie


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['reference', 'nom', 'categorie', 'fournisseur', 'description',
                  'prix_achat', 'prix_vente', 'quantite_stock', 'seuil_alerte', 'image']
        widgets = {
            'reference':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: CAM-001'}),
            'nom':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'categorie':      forms.Select(attrs={'class': 'form-select'}),
            'fournisseur':    forms.Select(attrs={'class': 'form-select'}),
            'description':    forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prix_achat':     forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'prix_vente':     forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'quantite_stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'seuil_alerte':   forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5'}),
            'image':          forms.FileInput(attrs={'class': 'form-control'}),
        }


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'telephone', 'email', 'adresse']
        widgets = {
            'nom':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du fournisseur'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+222 XX XX XX XX'}),
            'email':     forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'adresse':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'telephone', 'email', 'adresse']
        widgets = {
            'nom':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du client'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+222 XX XX XX XX'}),
            'email':     forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'adresse':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MouvementForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['produit', 'type_mouvement', 'quantite', 'motif']
        widgets = {
            'produit':        forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'quantite':       forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '1'}),
            'motif':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Raison du mouvement'}),
        }


class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['numero', 'client', 'date_validite', 'statut', 'notes']
        widgets = {
            'numero':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DEV-2026-001'}),
            'client':         forms.Select(attrs={'class': 'form-select'}),
            'date_validite':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut':         forms.Select(attrs={'class': 'form-select'}),
            'notes':          forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['numero', 'client', 'date_echeance', 'statut', 'notes']
        # ← PAS de 'devis' ici, c'est optionnel
        widgets = {
            'numero':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FAC-2026-001'}),
            'client':        forms.Select(attrs={'class': 'form-select'}),
            'date_echeance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut':        forms.Select(attrs={'class': 'form-select'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
        
        
class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['facture', 'montant', 'date_paiement', 'mode_paiement', 'reference', 'notes']
        widgets = {
            'facture':        forms.Select(attrs={'class': 'form-select'}),
            'montant':        forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'date_paiement':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mode_paiement':  forms.Select(attrs={'class': 'form-select'}),
            'reference':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'N° chèque, référence virement...'}),
            'notes':          forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }        
        
        
        
from .models import Installation, Maintenance, Contrat, Site

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['client', 'nom', 'adresse', 'latitude', 'longitude', 'description']
        widgets = {
            'client':      forms.Select(attrs={'class': 'form-select'}),
            'nom':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du site'}),
            'adresse':     forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'latitude':    forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '18.0783'}),
            'longitude':   forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '-15.9653'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class InstallationForm(forms.ModelForm):
    class Meta:
        model = Installation
        fields = ['reference', 'client', 'site', 'technicien', 'date_prevue',
                  'date_reelle', 'statut', 'description', 'notes', 'facture']
        widgets = {
            'reference':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INST-2026-001'}),
            'client':      forms.Select(attrs={'class': 'form-select'}),
            'site':        forms.Select(attrs={'class': 'form-select'}),
            'technicien':  forms.TextInput(attrs={'class': 'form-control'}),
            'date_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_reelle': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut':      forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes':       forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'facture':     forms.Select(attrs={'class': 'form-select'}),
        }

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = ['reference', 'client', 'site', 'installation', 'type_maintenance',
                  'priorite', 'statut', 'technicien', 'description', 'solution',
                  'date_signalement', 'date_intervention', 'date_resolution']
        widgets = {
            'reference':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SAV-2026-001'}),
            'client':            forms.Select(attrs={'class': 'form-select'}),
            'site':              forms.Select(attrs={'class': 'form-select'}),
            'installation':      forms.Select(attrs={'class': 'form-select'}),
            'type_maintenance':  forms.Select(attrs={'class': 'form-select'}),
            'priorite':          forms.Select(attrs={'class': 'form-select'}),
            'statut':            forms.Select(attrs={'class': 'form-select'}),
            'technicien':        forms.TextInput(attrs={'class': 'form-control'}),
            'description':       forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'solution':          forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_signalement':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_intervention': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_resolution':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = ['reference', 'client', 'type_contrat', 'statut',
                  'date_debut', 'date_fin', 'montant', 'description']
        widgets = {
            'reference':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CONT-2026-001'}),
            'client':       forms.Select(attrs={'class': 'form-select'}),
            'type_contrat': forms.Select(attrs={'class': 'form-select'}),
            'statut':       forms.Select(attrs={'class': 'form-select'}),
            'date_debut':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'montant':      forms.NumberInput(attrs={'class': 'form-control'}),
            'description':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }        