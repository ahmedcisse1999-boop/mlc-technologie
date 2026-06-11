# stock/models.py

from django.db import models
from django.utils import timezone

# ─────────────────────────────────────────
# 1. CATÉGORIE DE PRODUIT
# ─────────────────────────────────────────
class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Catégorie"

    def __str__(self):
        return self.nom


# ─────────────────────────────────────────
# 2. FOURNISSEUR
# ─────────────────────────────────────────
class Fournisseur(models.Model):
    nom = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fournisseur"

    def __str__(self):
        return self.nom


# ─────────────────────────────────────────
# 3. CLIENT
# ─────────────────────────────────────────
class Client(models.Model):
    nom = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"

    def __str__(self):
        return self.nom


# ─────────────────────────────────────────
# 4. PRODUIT (CAMÉRA)
# ─────────────────────────────────────────
class Produit(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    nom = models.CharField(max_length=200)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantite_stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=5)  # Alerte si stock < ce seuil
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Produit"

    def __str__(self):
        return f"{self.reference} - {self.nom}"

    @property
    def stock_bas(self):
        return self.quantite_stock <= self.seuil_alerte


# ─────────────────────────────────────────
# 5. MOUVEMENT DE STOCK (Entrée / Sortie)
# ─────────────────────────────────────────
class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
    ]
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    motif = models.CharField(max_length=255, blank=True)
    created_by = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        ordering = ['-date']

    def __str__(self):
        return f"{self.type_mouvement} - {self.produit.nom} ({self.quantite})"

    def save(self, *args, **kwargs):
        # Met à jour automatiquement le stock du produit
        if self.type_mouvement == 'entree':
            self.produit.quantite_stock += self.quantite
        elif self.type_mouvement == 'sortie':
            self.produit.quantite_stock -= self.quantite
        self.produit.save()
        super().save(*args, **kwargs)


# ─────────────────────────────────────────
# 6. DEVIS
# ─────────────────────────────────────────
class Devis(models.Model):
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoye', 'Envoyé'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
    ]
    numero = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validite = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Devis"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Devis {self.numero} - {self.client.nom}"

    @property
    def total(self):
        return sum(ligne.sous_total for ligne in self.lignes.all())


class LigneDevis(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire


# ─────────────────────────────────────────
# 7. FACTURE
# ─────────────────────────────────────────
class Facture(models.Model):
    STATUT_CHOICES = [
        ('non_payee', 'Non payée'),
        ('partiellement', 'Partiellement payée'),
        ('payee', 'Payée'),
    ]
    numero = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    devis = models.OneToOneField(Devis, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='non_payee')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Facture"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Facture {self.numero} - {self.client.nom}"

    @property
    def total(self):
        return sum(ligne.sous_total for ligne in self.lignes.all())
    
    
    @property
    def total_paye(self):
       from django.db.models import Sum
       result = self.paiements.aggregate(Sum('montant'))['montant__sum']
       return result or 0

    @property
    def reste_a_payer(self):
       return self.total - self.total_paye


class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire
    
    
    
    
    # Ajoute à la fin de models.py

class Paiement(models.Model):
    MODE_CHOICES = [
        ('especes',      'Espèces'),
        ('virement',     'Virement'),
        ('cheque',       'Chèque'),
        ('mobile_money', 'Mobile Money'),
    ]
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField()
    mode_paiement = models.CharField(max_length=20, choices=MODE_CHOICES, default='especes')
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paiement"
        ordering = ['-date_paiement']

    def __str__(self):
        return f"Paiement {self.montant} MRU — {self.facture.numero}"
    
    
    
    
    # Ajoute à la fin de models.py

class Vente(models.Model):
    facture   = models.OneToOneField('Facture', on_delete=models.CASCADE, related_name='vente')
    client    = models.ForeignKey(Client, on_delete=models.CASCADE)
    date      = models.DateTimeField(auto_now_add=True)
    total     = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=20, default='especes')

    class Meta:
        verbose_name = "Vente"
        ordering = ['-date']

    def __str__(self):
        return f"Vente {self.facture.numero} — {self.client.nom}"


class LigneVente(models.Model):
    vente         = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes')
    produit       = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite      = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire
    
    
    
from django.contrib.auth.models import User

class Profil(models.Model):
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    photo    = models.ImageField(upload_to='profils/', blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True)
    poste    = models.CharField(max_length=100, blank=True, default='Administrateur')

    def __str__(self):
        return f"Profil de {self.user.username}"   
    
    
    
    
    
    
# ─────────────────────────────────────────
# SITE CLIENT (lieu d'installation)
# ─────────────────────────────────────────
class Site(models.Model):
    client      = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sites')
    nom         = models.CharField(max_length=200)
    adresse     = models.TextField()
    latitude    = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude   = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    description = models.TextField(blank=True)
    date_ajout  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Site"

    def __str__(self):
        return f"{self.nom} — {self.client.nom}"


# ─────────────────────────────────────────
# INSTALLATION
# ─────────────────────────────────────────
class Installation(models.Model):
    STATUT_CHOICES = [
        ('planifie',   'Planifié'),
        ('en_cours',   'En cours'),
        ('termine',    'Terminé'),
        ('annule',     'Annulé'),
    ]
    reference    = models.CharField(max_length=100, unique=True)
    client       = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='installations')
    site         = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    produits     = models.ManyToManyField(Produit, blank=True)
    technicien   = models.CharField(max_length=200, blank=True)
    date_prevue  = models.DateField()
    date_reelle  = models.DateField(blank=True, null=True)
    statut       = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    description  = models.TextField(blank=True)
    notes        = models.TextField(blank=True)
    facture      = models.ForeignKey('Facture', on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Installation"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Installation {self.reference} — {self.client.nom}"


# ─────────────────────────────────────────
# MAINTENANCE / SAV
# ─────────────────────────────────────────
class Maintenance(models.Model):
    TYPE_CHOICES = [
        ('preventive',  'Préventive'),
        ('corrective',  'Corrective'),
        ('urgence',     'Urgence'),
    ]
    STATUT_CHOICES = [
        ('ouvert',      'Ouvert'),
        ('en_cours',    'En cours'),
        ('resolu',      'Résolu'),
        ('ferme',       'Fermé'),
    ]
    PRIORITE_CHOICES = [
        ('basse',   'Basse'),
        ('normale', 'Normale'),
        ('haute',   'Haute'),
        ('urgente', 'Urgente'),
    ]
    reference    = models.CharField(max_length=100, unique=True)
    client       = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='maintenances')
    site         = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True)
    installation = models.ForeignKey(Installation, on_delete=models.SET_NULL, null=True, blank=True)
    type_maintenance = models.CharField(max_length=20, choices=TYPE_CHOICES, default='corrective')
    priorite     = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='normale')
    statut       = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ouvert')
    technicien   = models.CharField(max_length=200, blank=True)
    description  = models.TextField()
    solution     = models.TextField(blank=True)
    date_signalement = models.DateField()
    date_intervention = models.DateField(blank=True, null=True)
    date_resolution   = models.DateField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Maintenance"
        ordering = ['-date_creation']

    def __str__(self):
        return f"SAV {self.reference} — {self.client.nom}"


# ─────────────────────────────────────────
# CONTRAT
# ─────────────────────────────────────────
class Contrat(models.Model):
    TYPE_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('surveillance','Surveillance'),
        ('installation','Installation'),
        ('autre',       'Autre'),
    ]
    STATUT_CHOICES = [
        ('actif',    'Actif'),
        ('expire',   'Expiré'),
        ('resilie',  'Résilié'),
        ('en_attente','En attente'),
    ]
    reference   = models.CharField(max_length=100, unique=True)
    client      = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contrats')
    type_contrat = models.CharField(max_length=20, choices=TYPE_CHOICES, default='maintenance')
    statut      = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    date_debut  = models.DateField()
    date_fin    = models.DateField()
    montant     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contrat"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Contrat {self.reference} — {self.client.nom}"

    @property
    def est_expire(self):
        from django.utils import timezone
        return self.date_fin < timezone.now().date()    