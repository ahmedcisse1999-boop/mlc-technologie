from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from decimal import Decimal, InvalidOperation
import traceback
from .models import Installation, Maintenance, Contrat, Site

from .models import (
    Produit, Fournisseur, Client, MouvementStock,
    Facture, LigneFacture, Devis, LigneDevis,
    Categorie, Paiement
)

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# ════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════
@login_required(login_url='/login/')
def dashboard(request):
    produits_alerte = [p for p in Produit.objects.all() if p.stock_bas]
    context = {
        'total_produits':      Produit.objects.count(),
        'total_clients':       Client.objects.count(),
        'total_fournisseurs':  Fournisseur.objects.count(),
        'total_factures':      Facture.objects.count(),
        'alertes_count':       len(produits_alerte),
        'produits_alerte':     produits_alerte[:5],
        'derniers_mouvements': MouvementStock.objects.select_related('produit').order_by('-date')[:8],
        'dernieres_factures':  Facture.objects.select_related('client').order_by('-date_creation')[:5],
    }
    return render(request, 'stock/dashboard.html', context)


# ════════════════════════════════════════
# PRODUITS
# ════════════════════════════════════════
def produit_liste(request):
    produits = Produit.objects.select_related('categorie', 'fournisseur').all()
    return render(request, 'stock/produit_liste.html', {'produits': produits})

def produit_ajouter(request):
    from .forms import ProduitForm
    form = ProduitForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Produit ajouté avec succès !")
        return redirect('stock:produit_liste')
    return render(request, 'stock/produit_form.html', {'form': form, 'titre': 'Ajouter un produit'})

def produit_modifier(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    from .forms import ProduitForm
    form = ProduitForm(request.POST or None, request.FILES or None, instance=produit)
    if form.is_valid():
        form.save()
        messages.success(request, "Produit modifié !")
        return redirect('stock:produit_liste')
    return render(request, 'stock/produit_form.html', {'form': form, 'titre': 'Modifier le produit'})

def produit_supprimer(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        messages.success(request, "Produit supprimé.")
        return redirect('stock:produit_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': produit})


def produit_detail(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    mouvements = MouvementStock.objects.filter(produit=produit).order_by('-date')[:10]
    return render(request, 'stock/produit_detail.html', {
        'produit': produit,
        'mouvements': mouvements,
    })


# ════════════════════════════════════════
# CATÉGORIES
# ════════════════════════════════════════
def categorie_liste(request):
    categories = Categorie.objects.all()
    return render(request, 'stock/categorie_liste.html', {'categories': categories})

def categorie_detail(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    return render(request, 'stock/categorie_detail.html', {'categorie': categorie})

def categorie_modifier(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    from .forms import CategorieForm
    form = CategorieForm(request.POST or None, instance=categorie)
    if form.is_valid():
        form.save()
        messages.success(request, "Catégorie modifiée !")
        return redirect('stock:categorie_liste')
    return render(request, 'stock/categorie_form.html', {
        'form': form, 'titre': 'Modifier la catégorie'
    })

def categorie_ajouter(request):
    from .forms import CategorieForm
    form = CategorieForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Catégorie ajoutée !")
        return redirect('stock:categorie_liste')
    return render(request, 'stock/categorie_form.html', {'form': form, 'titre': 'Ajouter une catégorie'})

def categorie_form(request):
    from .forms import CategorieForm
    form = CategorieForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        c = form.save()
        return JsonResponse({'id': c.pk, 'nom': c.nom, 'success': True})
    return JsonResponse({'success': False, 'errors': str(form.errors)})


# ════════════════════════════════════════
# FOURNISSEURS
# ════════════════════════════════════════
def fournisseur_liste(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'stock/fournisseur_liste.html', {'fournisseurs': fournisseurs})


def fournisseur_detail(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    return render(request, 'stock/fournisseur_detail.html', {
        'fournisseur': fournisseur
    })

def fournisseur_ajouter(request):
    from .forms import FournisseurForm
    form = FournisseurForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Fournisseur ajouté !")
        return redirect('stock:fournisseur_liste')
    return render(request, 'stock/fournisseur_form.html', {'form': form, 'titre': 'Ajouter un fournisseur'})

def fournisseur_modifier(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    from .forms import FournisseurForm
    form = FournisseurForm(request.POST or None, instance=fournisseur)
    if form.is_valid():
        form.save()
        messages.success(request, "Fournisseur modifié !")
        return redirect('stock:fournisseur_liste')
    return render(request, 'stock/fournisseur_form.html', {'form': form, 'titre': 'Modifier fournisseur'})

def fournisseur_supprimer(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        messages.success(request, "Fournisseur supprimé.")
        return redirect('stock:fournisseur_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': fournisseur})

def fournisseur_form(request):
    from .forms import FournisseurForm
    form = FournisseurForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        f = form.save()
        return JsonResponse({'id': f.pk, 'nom': f.nom, 'success': True})
    return JsonResponse({'success': False, 'errors': str(form.errors)})


# ════════════════════════════════════════
# CLIENTS
# ════════════════════════════════════════
def client_liste(request):
    clients = Client.objects.all()
    return render(request, 'stock/client_liste.html', {'clients': clients})


def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'stock/client_detail.html', {'client': client})

def client_ajouter(request):
    from .forms import ClientForm
    form = ClientForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Client ajouté !")
        return redirect('stock:client_liste')
    return render(request, 'stock/client_form.html', {'form': form, 'titre': 'Ajouter un client'})

def client_modifier(request, pk):
    client = get_object_or_404(Client, pk=pk)
    from .forms import ClientForm
    form = ClientForm(request.POST or None, instance=client)
    if form.is_valid():
        form.save()
        messages.success(request, "Client modifié !")
        return redirect('stock:client_liste')
    return render(request, 'stock/client_form.html', {'form': form, 'titre': 'Modifier client'})

def client_supprimer(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, "Client supprimé.")
        return redirect('stock:client_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': client})

def client_form(request):
    from .forms import ClientForm
    form = ClientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        c = form.save()
        return JsonResponse({'id': c.pk, 'nom': c.nom, 'success': True})
    return JsonResponse({'success': False, 'errors': str(form.errors)})


# ════════════════════════════════════════
# MOUVEMENTS
# ════════════════════════════════════════


def mouvement_ajouter(request):
    from .forms import MouvementForm
    form = MouvementForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Mouvement enregistré !")
        return redirect('stock:mouvement_liste')
    return render(request, 'stock/mouvement_form.html', {'form': form, 'titre': 'Nouveau mouvement'})



def mouvement_detail(request, pk):
    mouvement = get_object_or_404(MouvementStock, pk=pk)
    return render(request, 'stock/mouvement_detail.html', {'mouvement': mouvement})

def mouvement_modifier(request, pk):
    mouvement = get_object_or_404(MouvementStock, pk=pk)
    from .forms import MouvementForm
    form = MouvementForm(request.POST or None, instance=mouvement)
    if form.is_valid():
        form.save()
        messages.success(request, "Mouvement modifié !")
        return redirect('stock:mouvement_liste')
    return render(request, 'stock/mouvement_form.html', {
        'form': form, 'titre': 'Modifier le mouvement'
    })

def mouvement_supprimer(request, pk):
    mouvement = get_object_or_404(MouvementStock, pk=pk)
    if request.method == 'POST':
        mouvement.delete()
        messages.success(request, "Mouvement supprimé.")
        return redirect('stock:mouvement_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': mouvement})

def mouvement_liste(request):
    mouvements = MouvementStock.objects.select_related('produit').order_by('-date')
    context = {
        'mouvements': mouvements,
        'nb_entrees': mouvements.filter(type_mouvement='entree').count(),
        'nb_sorties': mouvements.filter(type_mouvement='sortie').count(),
    }
    return render(request, 'stock/mouvement_liste.html', context)

# ════════════════════════════════════════
# ALERTES
# ════════════════════════════════════════
def alertes(request):
    produits_alerte = [p for p in Produit.objects.all() if p.stock_bas]
    return render(request, 'stock/alertes.html', {
        'produits_alerte': produits_alerte,
        'alertes_count': len(produits_alerte),
    })


# ════════════════════════════════════════
# FACTURES
# ════════════════════════════════════════
def facture_liste(request):
    factures = Facture.objects.select_related('client').order_by('-date_creation')
    return render(request, 'stock/facture_liste.html', {'factures': factures})


def facture_ajouter(request):
    from .forms import FactureForm

    if request.method == 'POST':
        form = FactureForm(request.POST)
        if form.is_valid():
            facture = form.save()

            produits_ids = request.POST.getlist('ligne_produit[]')
            qtites       = request.POST.getlist('ligne_quantite[]')
            prix_list    = request.POST.getlist('ligne_prix[]')
            remises      = request.POST.getlist('ligne_remise[]')

            lignes_creees = 0
            for i, produit_id in enumerate(produits_ids):
                produit_id = str(produit_id).strip()
                if not produit_id:
                    continue
                try:
                    p = Produit.objects.get(pk=int(produit_id))
                    qte = int(qtites[i]) if i < len(qtites) and str(qtites[i]).strip() else 1
                    try:
                        prix_u = Decimal(str(prix_list[i])) if i < len(prix_list) and str(prix_list[i]).strip() else p.prix_vente
                    except InvalidOperation:
                        prix_u = p.prix_vente
                    try:
                        remise = Decimal(str(remises[i])) if i < len(remises) and str(remises[i]).strip() else Decimal('0')
                    except InvalidOperation:
                        remise = Decimal('0')
                    prix_final = prix_u * (1 - remise / 100)
                    LigneFacture.objects.create(
                        facture=facture,
                        produit=p,
                        quantite=qte,
                        prix_unitaire=prix_final,
                    )
                    lignes_creees += 1
                except Exception as e:
                    traceback.print_exc()
                    continue

            messages.success(request, f"Facture {facture.numero} créée avec {lignes_creees} ligne(s) !")
            return redirect('stock:facture_detail', pk=facture.pk)
        else:
            messages.error(request, f"Erreur : {form.errors}")
    else:
        form = FactureForm()

    return render(request, 'stock/facture_form_avance.html', {
        'form': form,
        'produits': Produit.objects.all(),
        'clients': Client.objects.all(),
        'titre': 'Nouvelle facture',
    })


def facture_detail(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    return render(request, 'stock/facture_detail.html', {'facture': facture})

def facture_modifier(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    from .forms import FactureForm
    form = FactureForm(request.POST or None, instance=facture)
    if form.is_valid():
        form.save()
        messages.success(request, "Facture modifiée !")
        return redirect('stock:facture_detail', pk=facture.pk)
    return render(request, 'stock/facture_form_avance.html', {
        'form': form, 'facture': facture,
        'produits': Produit.objects.all(),
        'titre': 'Modifier la facture'
    })

def facture_supprimer(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    if request.method == 'POST':
        facture.delete()
        messages.success(request, "Facture supprimée.")
        return redirect('stock:facture_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': facture})

def facture_pdf(request, pk):
    import os
    from django.conf import settings
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                     Paragraph, Spacer, HRFlowable, Image)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

    facture = get_object_or_404(Facture, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Facture_{facture.numero}.pdf"'

    doc = SimpleDocTemplate(
        response, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=2*cm
    )

    # ── Couleurs MLC ──
    VERT       = colors.HexColor('#1a7a2e')
    VERT_LIGHT = colors.HexColor('#e8f5eb')
    NAVY       = colors.HexColor('#0d2461')
    ORANGE     = colors.HexColor('#e8520a')
    GRIS       = colors.HexColor('#f8fafc')
    GRIS_BORD  = colors.HexColor('#e2e8f0')
    BLANC      = colors.white

    styles = getSampleStyleSheet()

    def style(name, **kwargs):
        s = ParagraphStyle(name, **kwargs)
        return s

    elements = []

    # ════════════════════════════════════════
    # EN-TÊTE : Logo + Titre FACTURE
    # ════════════════════════════════════════
    logo_path = None
    for ext in ['logo_mlc.jpeg', 'logo_mlc.jpg', 'logo_mlc.png']:
       p = os.path.join(settings.BASE_DIR, 'static', 'img', ext)
       if os.path.exists(p):
           logo_path = p
           break
        

    # Colonne logo
    
    # Colonne logo
    if logo_path:
        col_logo = Image(logo_path, width=2.8*cm, height=2.3*cm)
    else:
        col_logo = Paragraph(
        '<font size=15 color="#1a7a2e"><b>MLC</b></font>'
        '<font size=12 color="#e8520a"> Technologies Rim</font>',
        style('LogoText', fontName='Helvetica-Bold', fontSize=20)
    )

# Colonne droite — FACTURE bien séparé
    col_droite_data = [
    [Paragraph('', style('ESP'))],  # espace vide pour aligner
    [Paragraph(
        '<font size=15 color="#1a7a2e"><b>FACTURE</b></font>',
        style('FT', fontName='Helvetica-Bold', alignment=2)
    )],
    [Paragraph(
        f'<font size=10 color="#0d2461"><b>N° {facture.numero}</b></font>',
        style('FN', fontName='Helvetica-Bold', alignment=2)
    )],
    [Paragraph(
        f'<font size=9 color="#475569">Date : {facture.date_creation.strftime("%d/%m/%Y")}</font>',
        style('FD', alignment=2)
    )],
    [Paragraph(
        f'<font size=9 color="#475569">Échéance : {facture.date_echeance.strftime("%d/%m/%Y")}</font>',
        style('FE', alignment=2)
    )],
]
    tbl_droite = Table(col_droite_data, colWidths=[8.5*cm])
    tbl_droite.setStyle(TableStyle([
    ('ALIGN',         (0,0), (-1,-1), 'RIGHT'),
    ('TOPPADDING',    (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    # ← PAS de LINEBELOW ici
]))

    header_tbl = Table(
    [[col_logo, tbl_droite]],
    colWidths=[9.5*cm, 8.5*cm]
)
    header_tbl.setStyle(TableStyle([
    ('VALIGN', (0,0), (0,0), 'TOP'),   # logo en haut
    ('VALIGN', (1,0), (1,0), 'TOP'),   # titre en haut
    ('ALIGN',  (1,0), (1,0), 'RIGHT'),
]))
    elements.append(header_tbl)
    elements.append(Spacer(1, 0.3*cm))
    
    # Infos entreprise sous logo
    infos_entreprise = Table([[
        Paragraph(
            '<font size=8 color="#475569">Nouakchott, Mauritanie &nbsp;|&nbsp; '
            'Tél : +222 49 71 79 05 &nbsp;|&nbsp; Email : contact@mlc-tech.mr</font>',
            style('IE')
        )
    ]], colWidths=[18*cm])
    elements.append(infos_entreprise)

    # Ligne séparatrice
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width='100%', thickness=2, color=VERT, spaceAfter=0.4*cm))

    # ════════════════════════════════════════
    # BLOC CLIENT + STATUT
    # ════════════════════════════════════════
    # Statut couleur et texte
    statut_txt = facture.get_statut_display().upper()
    if facture.statut == 'payee':
         statut_hex = '#1a7a2e'
    elif facture.statut == 'partiellement':
         statut_hex = '#e8520a'
    else:
        statut_hex = '#ef4444'

    client_info = [
        [Paragraph('<font size=8 color="#1a7a2e"><b>FACTURÉ À</b></font>', style('CI'))],
        [Paragraph(f'<font size=13 color="#0d2461"><b>{facture.client.nom}</b></font>', style('CN', fontName='Helvetica-Bold'))],
    ]
    if facture.client.telephone:
        client_info.append([Paragraph(f'<font size=9 color="#475569">Tél : {facture.client.telephone}</font>', style('CT'))])
    if facture.client.email:
        client_info.append([Paragraph(f'<font size=9 color="#475569">Email : {facture.client.email}</font>', style('CE'))])
    if facture.client.adresse:
        client_info.append([Paragraph(f'<font size=9 color="#475569">{facture.client.adresse}</font>', style('CA'))])

    tbl_client = Table(client_info, colWidths=[10*cm])
    tbl_client.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), VERT_LIGHT),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEAFTER', (0,0), (0,-1), 3, VERT),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [VERT_LIGHT]),
    ]))

    # Statut badge
    tbl_statut = Table([
    [Paragraph('<font size=8 color="#475569">STATUT</font>', style('SS'))],
    [Paragraph(f'<font size=12 color="{statut_hex}"><b>{statut_txt}</b></font>',
               style('SV', fontName='Helvetica-Bold'))],
    [Paragraph(f'<font size=8 color="#475569">Lignes : {facture.lignes.count()}</font>', style('SL'))],
], colWidths=[7.5*cm])
    tbl_statut.setStyle(TableStyle([
    ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
    ('BACKGROUND',   (0,0), (-1,-1), GRIS),
    ('TOPPADDING',   (0,0), (-1,-1), 8),
    ('BOTTOMPADDING',(0,0), (-1,-1), 8),
    ('BOX',          (0,0), (-1,-1), 0.5, GRIS_BORD),
]))

    bloc_client = Table([[tbl_client, '', tbl_statut]], colWidths=[10*cm, 0.5*cm, 7.5*cm])
    elements.append(bloc_client)
    elements.append(Spacer(1, 0.5*cm))

    # ════════════════════════════════════════
    # TABLEAU DES LIGNES
    # ════════════════════════════════════════
    entetes = ['#', 'PRODUIT', 'RÉFÉRENCE', 'PRIX UNITAIRE', 'QTÉ', 'SOUS-TOTAL']
    data = [entetes]

    for i, ligne in enumerate(facture.lignes.all(), 1):
        data.append([
            str(i),
            ligne.produit.nom,
            ligne.produit.reference,
            f'{ligne.prix_unitaire:,.2f} MRU',
            str(ligne.quantite),
            f'{ligne.sous_total:,.2f} MRU',
        ])

    # Ligne vide si pas de lignes
    if len(data) == 1:
        data.append(['', 'Aucune ligne', '', '', '', ''])

    tbl_lignes = Table(data, colWidths=[0.8*cm, 5.5*cm, 3*cm, 3.2*cm, 1.2*cm, 3.3*cm])
    tbl_lignes.setStyle(TableStyle([
        # Header
        ('BACKGROUND',   (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',    (0,0), (-1,0), BLANC),
        ('FONTNAME',     (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0,0), (-1,0), 9),
        ('ALIGN',        (0,0), (-1,0), 'CENTER'),
        ('TOPPADDING',   (0,0), (-1,0), 9),
        ('BOTTOMPADDING',(0,0), (-1,0), 9),

        # Rows
        ('FONTSIZE',     (0,1), (-1,-1), 9),
        ('TOPPADDING',   (0,1), (-1,-1), 7),
        ('BOTTOMPADDING',(0,1), (-1,-1), 7),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [BLANC, GRIS]),

        # Alignements
        ('ALIGN',  (0,0), (0,-1), 'CENTER'),   # #
        ('ALIGN',  (3,1), (3,-1), 'RIGHT'),    # Prix
        ('ALIGN',  (4,1), (4,-1), 'CENTER'),   # Qté
        ('ALIGN',  (5,1), (5,-1), 'RIGHT'),    # Sous-total

        # Bordures
        ('GRID',   (0,0), (-1,-1), 0.3, GRIS_BORD),
        ('LINEBELOW', (0,0), (-1,0), 1.5, NAVY),
        ('LINEBEFORE', (5,0), (5,-1), 1, GRIS_BORD),
    ]))
    elements.append(tbl_lignes)
    elements.append(Spacer(1, 0.4*cm))

    # ════════════════════════════════════════
    # TOTAUX
    # ════════════════════════════════════════
    total = facture.total
    total_paye = facture.total_paye
    reste = facture.reste_a_payer

    totaux_data = [
        ['', 'Sous-total HT',    f'{total:,.2f} MRU'],
        ['', 'Total payé',       f'{total_paye:,.2f} MRU'],
        ['', 'Reste à payer',    f'{reste:,.2f} MRU'],
        ['', 'TOTAL TTC',        f'{total:,.2f} MRU'],
    ]

    tbl_totaux = Table(totaux_data, colWidths=[9.5*cm, 5*cm, 3.5*cm])
    tbl_totaux.setStyle(TableStyle([
        ('ALIGN',       (1,0), (2,-1), 'RIGHT'),
        ('FONTSIZE',    (0,0), (-1,-2), 9),
        ('TEXTCOLOR',   (0,0), (-1,-2), colors.HexColor('#475569')),
        ('TOPPADDING',  (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),

        # Ligne Total payé
        ('TEXTCOLOR',   (1,1), (2,1), VERT),
        ('FONTNAME',    (1,1), (2,1), 'Helvetica-Bold'),

        # Ligne Reste
        ('TEXTCOLOR',   (1,2), (2,2), ORANGE),
        ('FONTNAME',    (1,2), (2,2), 'Helvetica-Bold'),

        # Ligne TOTAL TTC
        ('BACKGROUND',  (1,3), (2,3), NAVY),
        ('TEXTCOLOR',   (1,3), (2,3), BLANC),
        ('FONTNAME',    (1,3), (2,3), 'Helvetica-Bold'),
        ('FONTSIZE',    (1,3), (2,3), 11),
        ('TOPPADDING',  (1,3), (2,3), 9),
        ('BOTTOMPADDING',(1,3),(2,3), 9),
        ('LINEABOVE',   (1,3), (2,3), 1.5, VERT),
    ]))
    elements.append(tbl_totaux)

    # ════════════════════════════════════════
    # NOTES
    # ════════════════════════════════════════
    if facture.notes:
        elements.append(Spacer(1, 0.4*cm))
        notes_tbl = Table([[
            Paragraph(f'<font size=8 color="#475569"><b>NOTES :</b> {facture.notes}</font>',
                      style('Notes'))
        ]], colWidths=[18*cm])
        notes_tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), GRIS),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LINEAFTER', (0,0), (0,0), 3, ORANGE),
        ]))
        elements.append(notes_tbl)

    # ════════════════════════════════════════
    # PIED DE PAGE
    # ════════════════════════════════════════
    elements.append(Spacer(1, 0.6*cm))
    elements.append(HRFlowable(width='100%', thickness=1, color=GRIS_BORD))
    elements.append(Spacer(1, 0.2*cm))
    footer_tbl = Table([[
        Paragraph('<font size=8 color="#94a3b8">MLC Technologies Rim — Nouakchott, Mauritanie</font>',
                  style('FL')),
        Paragraph('<font size=8 color="#94a3b8">+222 49 71 79 05</font>',
                  style('FC')),
        Paragraph(f'<font size=8 color="#94a3b8">Facture générée le {facture.date_creation.strftime("%d/%m/%Y")}</font>',
                  style('FR')),
    ]], colWidths=[6*cm, 6*cm, 6*cm])
    footer_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
    ]))
    elements.append(footer_tbl)

    doc.build(elements)
    return response


# ════════════════════════════════════════
# PAIEMENTS
# ════════════════════════════════════════

# Ajoute dans views.py

def paiement_liste(request):
    from .models import Paiement
    paiements = Paiement.objects.select_related(
        'facture', 'facture__client'
    ).order_by('-date_paiement')
    return render(request, 'stock/paiement_liste.html', {'paiements': paiements})


def paiement_ajouter(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    from .forms import PaiementForm
    from .models import Vente, LigneVente

    form = PaiementForm(request.POST or None, initial={
        'facture': facture,
        'montant': facture.reste_a_payer
    })

    if form.is_valid():
        paiement = form.save()

        # Recalcule le total payé
        total_paye = sum(p.montant for p in facture.paiements.all())

        if total_paye >= facture.total:
            facture.statut = 'payee'

            # ══ Créer la vente automatiquement ══
            if not hasattr(facture, 'vente'):
                vente = Vente.objects.create(
                    facture=facture,
                    client=facture.client,
                    total=facture.total,
                    mode_paiement=paiement.mode_paiement,
                )
                # Créer les lignes de vente + déduire le stock
                for ligne in facture.lignes.all():
                    LigneVente.objects.create(
                        vente=vente,
                        produit=ligne.produit,
                        quantite=ligne.quantite,
                        prix_unitaire=ligne.prix_unitaire,
                    )
                    # ══ Déduire du stock automatiquement ══
                    ligne.produit.quantite_stock -= ligne.quantite
                    if ligne.produit.quantite_stock < 0:
                        ligne.produit.quantite_stock = 0
                    ligne.produit.save()

                    # Enregistrer le mouvement de sortie
                    MouvementStock.objects.create(
                        produit=ligne.produit,
                        type_mouvement='sortie',
                        quantite=ligne.quantite,
                        motif=f"Vente facture {facture.numero}",
                    )

                messages.success(request, f"✅ Paiement validé ! Vente enregistrée et stock mis à jour.")
            else:
                messages.success(request, f"Paiement de {paiement.montant} MRU enregistré !")
        else:
            facture.statut = 'partiellement'
            messages.success(request, f"Paiement partiel de {paiement.montant} MRU enregistré !")

        facture.save()
        return redirect('stock:facture_detail', pk=facture.pk)

    return render(request, 'stock/paiement_form.html', {
        'form': form,
        'facture': facture
    })

def vente_liste(request):
    from .models import Vente
    ventes = Vente.objects.select_related('client', 'facture').order_by('-date')
    total_ventes = sum(v.total for v in ventes)
    return render(request, 'stock/vente_liste.html', {
        'ventes': ventes,
        'total_ventes': total_ventes,
    })

# ════════════════════════════════════════
# DEVIS
# ════════════════════════════════════════
def devis_liste(request):
    devis = Devis.objects.select_related('client').order_by('-date_creation')
    return render(request, 'stock/devis_liste.html', {'devis_list': devis})

def devis_ajouter(request):
    from .forms import DevisForm
    if request.method == 'POST':
        form = DevisForm(request.POST)
        if form.is_valid():
            devis = form.save()
            produits_ids = request.POST.getlist('ligne_produit[]')
            qtites       = request.POST.getlist('ligne_quantite[]')
            prix_list    = request.POST.getlist('ligne_prix[]')
            for i, produit_id in enumerate(produits_ids):
                produit_id = str(produit_id).strip()
                if not produit_id:
                    continue
                try:
                    p = Produit.objects.get(pk=int(produit_id))
                    qte = int(qtites[i]) if i < len(qtites) and str(qtites[i]).strip() else 1
                    try:
                        prix_u = Decimal(str(prix_list[i])) if i < len(prix_list) and str(prix_list[i]).strip() else p.prix_vente
                    except InvalidOperation:
                        prix_u = p.prix_vente
                    LigneDevis.objects.create(devis=devis, produit=p, quantite=qte, prix_unitaire=prix_u)
                except Exception:
                    traceback.print_exc()
                    continue
            messages.success(request, f"Devis {devis.numero} créé !")
            return redirect('stock:devis_detail', pk=devis.pk)
        else:
            messages.error(request, f"Erreur : {form.errors}")
    else:
        form = DevisForm()
    return render(request, 'stock/devis_form_avance.html', {
        'form': form,
        'produits': Produit.objects.all(),
        'clients': Client.objects.all(),
        'titre': 'Nouveau devis',
    })

def devis_accepter(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    if request.method == 'POST':
        devis.statut = 'accepte'
        devis.save()
        messages.success(request, f"Devis {devis.numero} marqué comme accepté !")
    return redirect('stock:devis_detail', pk=devis.pk)

def devis_detail(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    return render(request, 'stock/devis_detail.html', {'devis': devis})

def devis_modifier(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    from .forms import DevisForm
    form = DevisForm(request.POST or None, instance=devis)
    if form.is_valid():
        devis = form.save()
        devis.lignes.all().delete()
        produits_ids = request.POST.getlist('ligne_produit[]')
        qtites       = request.POST.getlist('ligne_quantite[]')
        prix_list    = request.POST.getlist('ligne_prix[]')
        for i, produit_id in enumerate(produits_ids):
            produit_id = str(produit_id).strip()
            if not produit_id:
                continue
            try:
                p = Produit.objects.get(pk=int(produit_id))
                qte = int(qtites[i]) if i < len(qtites) and str(qtites[i]).strip() else 1
                try:
                    prix_u = Decimal(str(prix_list[i])) if i < len(prix_list) and str(prix_list[i]).strip() else p.prix_vente
                except InvalidOperation:
                    prix_u = p.prix_vente
                LigneDevis.objects.create(devis=devis, produit=p, quantite=qte, prix_unitaire=prix_u)
            except Exception:
                continue
        messages.success(request, "Devis modifié !")
        return redirect('stock:devis_detail', pk=devis.pk)
    return render(request, 'stock/devis_form_avance.html', {
        'form': form, 'devis': devis,
        'produits': Produit.objects.all(),
        'titre': 'Modifier le devis'
    })

def devis_supprimer(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    if request.method == 'POST':
        devis.delete()
        messages.success(request, "Devis supprimé.")
        return redirect('stock:devis_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': devis})

def devis_pdf(request, pk):
    import os
    from django.conf import settings
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                     Paragraph, Spacer, HRFlowable, Image)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

    devis = get_object_or_404(Devis, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Devis_{devis.numero}.pdf"'

    doc = SimpleDocTemplate(
        response, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=2*cm
    )

    # ── Couleurs MLC ──
    VERT       = colors.HexColor('#1a7a2e')
    VERT_LIGHT = colors.HexColor('#e8f5eb')
    NAVY       = colors.HexColor('#0d2461')
    ORANGE     = colors.HexColor('#e8520a')
    GRIS       = colors.HexColor('#f8fafc')
    GRIS_BORD  = colors.HexColor('#e2e8f0')
    BLANC      = colors.white

    def style(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    elements = []

    # ════════════════════════════════════════
    # EN-TÊTE : Logo + Titre DEVIS
    # ════════════════════════════════════════
    logo_path = None
    for ext in ['logo_mlc.jpeg', 'logo_mlc.jpg', 'logo_mlc.png']:
        p = os.path.join(settings.BASE_DIR, 'static', 'img', ext)
        if os.path.exists(p):
            logo_path = p
            break

    if logo_path:
        col_logo = Image(logo_path, width=2.8*cm, height=2.3*cm)
    else:
        col_logo = Paragraph(
            '<font size=20 color="#1a7a2e"><b>MLC</b></font>'
            '<font size=12 color="#e8520a"> Technologies Rim</font>',
            style('LogoText', fontName='Helvetica-Bold', fontSize=20)
        )

    # Colonne droite DEVIS
    col_droite_data = [
        [Paragraph('', style('ESP'))],
        [Paragraph(
            '<font size=15 color="#1a7a2e"><b>DEVIS</b></font>',
            style('FT', fontName='Helvetica-Bold', alignment=2)
        )],
        [Paragraph(
            f'<font size=13 color="#0d2461"><b>N° {devis.numero}</b></font>',
            style('FN', fontName='Helvetica-Bold', alignment=2)
        )],
        [Paragraph(
            f'<font size=9 color="#475569">Date : {devis.date_creation.strftime("%d/%m/%Y")}</font>',
            style('FD', alignment=2)
        )],
        [Paragraph(
            f'<font size=9 color="#475569">Valide jusqu\'au : {devis.date_validite.strftime("%d/%m/%Y")}</font>',
            style('FE', alignment=2)
        )],
    ]
    tbl_droite = Table(col_droite_data, colWidths=[8.5*cm])
    tbl_droite.setStyle(TableStyle([
        ('ALIGN',         (0,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING',    (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))

    header_tbl = Table(
        [[col_logo, tbl_droite]],
        colWidths=[9.5*cm, 8.5*cm]
    )
    header_tbl.setStyle(TableStyle([
        ('VALIGN', (0,0), (0,0), 'TOP'),
        ('VALIGN', (1,0), (1,0), 'TOP'),
        ('ALIGN',  (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(header_tbl)
    elements.append(Spacer(1, 0.3*cm))

    # Infos entreprise
    infos_tbl = Table([[
        Paragraph(
            '<font size=8 color="#475569">Nouakchott, Mauritanie &nbsp;|&nbsp; '
            'Tél : +222 49 71 79 05 &nbsp;|&nbsp; Email : contact@mlc-tech.mr</font>',
            style('IE')
        )
    ]], colWidths=[18*cm])
    elements.append(infos_tbl)
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width='100%', thickness=2, color=VERT, spaceAfter=0.4*cm))

    # ════════════════════════════════════════
    # BLOC CLIENT + STATUT
    # ════════════════════════════════════════
    statut_txt = devis.get_statut_display().upper()
    if devis.statut == 'accepte':
        statut_hex = '#1a7a2e'
    elif devis.statut == 'refuse':
        statut_hex = '#ef4444'
    elif devis.statut == 'envoye':
        statut_hex = '#0d2461'
    else:
        statut_hex = '#475569'

    client_info = [
        [Paragraph('<font size=8 color="#1a7a2e"><b>CLIENT</b></font>', style('CI'))],
        [Paragraph(f'<font size=13 color="#0d2461"><b>{devis.client.nom}</b></font>',
                   style('CN', fontName='Helvetica-Bold'))],
    ]
    if devis.client.telephone:
        client_info.append([Paragraph(
            f'<font size=9 color="#475569">Tél : {devis.client.telephone}</font>', style('CT'))])
    if devis.client.email:
        client_info.append([Paragraph(
            f'<font size=9 color="#475569">Email : {devis.client.email}</font>', style('CE'))])
    if devis.client.adresse:
        client_info.append([Paragraph(
            f'<font size=9 color="#475569">{devis.client.adresse}</font>', style('CA'))])

    tbl_client = Table(client_info, colWidths=[10*cm])
    tbl_client.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), VERT_LIGHT),
        ('LEFTPADDING',   (0,0), (-1,-1), 12),
        ('RIGHTPADDING',  (0,0), (-1,-1), 12),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEAFTER',     (0,0), (0,-1), 3, VERT),
    ]))

    tbl_statut = Table([
        [Paragraph('<font size=8 color="#475569">STATUT</font>', style('SS'))],
        [Paragraph(f'<font size=12 color="{statut_hex}"><b>{statut_txt}</b></font>',
                   style('SV', fontName='Helvetica-Bold'))],
        [Paragraph(f'<font size=8 color="#475569">Lignes : {devis.lignes.count()}</font>',
                   style('SL'))],
        [Paragraph(f'<font size=8 color="#475569">Total : {devis.total:,.2f} MRU</font>',
                   style('ST'))],
    ], colWidths=[7.5*cm])
    tbl_statut.setStyle(TableStyle([
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('BACKGROUND',    (0,0), (-1,-1), GRIS),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BOX',           (0,0), (-1,-1), 0.5, GRIS_BORD),
    ]))

    bloc_client = Table([[tbl_client, '', tbl_statut]], colWidths=[10*cm, 0.5*cm, 7.5*cm])
    elements.append(bloc_client)
    elements.append(Spacer(1, 0.5*cm))

    # ════════════════════════════════════════
    # TABLEAU DES LIGNES
    # ════════════════════════════════════════
    entetes = ['#', 'PRODUIT', 'RÉFÉRENCE', 'PRIX UNITAIRE', 'QTÉ', 'SOUS-TOTAL']
    data = [entetes]

    for i, ligne in enumerate(devis.lignes.all(), 1):
        data.append([
            str(i),
            ligne.produit.nom,
            ligne.produit.reference,
            f'{ligne.prix_unitaire:,.2f} MRU',
            str(ligne.quantite),
            f'{ligne.sous_total:,.2f} MRU',
        ])

    if len(data) == 1:
        data.append(['', 'Aucune ligne', '', '', '', ''])

    tbl_lignes = Table(data, colWidths=[0.8*cm, 5.5*cm, 3*cm, 3.2*cm, 1.2*cm, 3.3*cm])
    tbl_lignes.setStyle(TableStyle([
        # Header
        ('BACKGROUND',    (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0), BLANC),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0), 9),
        ('ALIGN',         (0,0), (-1,0), 'CENTER'),
        ('TOPPADDING',    (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 9),
        # Rows
        ('FONTSIZE',      (0,1), (-1,-1), 9),
        ('TOPPADDING',    (0,1), (-1,-1), 7),
        ('BOTTOMPADDING', (0,1), (-1,-1), 7),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [BLANC, GRIS]),
        # Alignements
        ('ALIGN',  (0,0), (0,-1), 'CENTER'),
        ('ALIGN',  (3,1), (3,-1), 'RIGHT'),
        ('ALIGN',  (4,1), (4,-1), 'CENTER'),
        ('ALIGN',  (5,1), (5,-1), 'RIGHT'),
        # Bordures
        ('GRID',      (0,0), (-1,-1), 0.3, GRIS_BORD),
        ('LINEBELOW', (0,0), (-1,0),  1.5, NAVY),
    ]))
    elements.append(tbl_lignes)
    elements.append(Spacer(1, 0.4*cm))

    # ════════════════════════════════════════
    # TOTAL
    # ════════════════════════════════════════
    total = devis.total
    totaux_data = [
        ['', 'Sous-total HT', f'{total:,.2f} MRU'],
        ['', 'TOTAL TTC',     f'{total:,.2f} MRU'],
    ]
    tbl_totaux = Table(totaux_data, colWidths=[9.5*cm, 5*cm, 3.5*cm])
    tbl_totaux.setStyle(TableStyle([
        ('ALIGN',         (1,0), (2,-1), 'RIGHT'),
        ('FONTSIZE',      (0,0), (-1,-2), 9),
        ('TEXTCOLOR',     (0,0), (-1,-2), colors.HexColor('#475569')),
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        # Ligne TOTAL TTC
        ('BACKGROUND',    (1,1), (2,1), NAVY),
        ('TEXTCOLOR',     (1,1), (2,1), BLANC),
        ('FONTNAME',      (1,1), (2,1), 'Helvetica-Bold'),
        ('FONTSIZE',      (1,1), (2,1), 11),
        ('TOPPADDING',    (1,1), (2,1), 9),
        ('BOTTOMPADDING', (1,1), (2,1), 9),
        ('LINEABOVE',     (1,1), (2,1), 1.5, VERT),
    ]))
    elements.append(tbl_totaux)

    # ════════════════════════════════════════
    # NOTES
    # ════════════════════════════════════════
    if devis.notes:
        elements.append(Spacer(1, 0.4*cm))
        notes_tbl = Table([[
            Paragraph(
                f'<font size=8 color="#475569"><b>NOTES :</b> {devis.notes}</font>',
                style('Notes')
            )
        ]], colWidths=[18*cm])
        notes_tbl.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), GRIS),
            ('LEFTPADDING',   (0,0), (-1,-1), 12),
            ('TOPPADDING',    (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LINEBEFORE',    (0,0), (0,0),   3, ORANGE),
        ]))
        elements.append(notes_tbl)

    # ════════════════════════════════════════
    # CONDITIONS
    # ════════════════════════════════════════
    elements.append(Spacer(1, 0.5*cm))
    conditions_tbl = Table([[
        Paragraph(
            '<font size=8 color="#475569"><b>CONDITIONS :</b> '
            'Ce devis est valable jusqu\'à la date indiquée. '
            'Tout accord sur ce devis entraîne l\'acceptation de nos conditions générales de vente.</font>',
            style('Cond')
        )
    ]], colWidths=[18*cm])
    conditions_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), colors.HexColor('#fffbeb')),
        ('LEFTPADDING',   (0,0), (-1,-1), 12),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBEFORE',    (0,0), (0,0),   3, ORANGE),
    ]))
    elements.append(conditions_tbl)

    # ════════════════════════════════════════
    # PIED DE PAGE
    # ════════════════════════════════════════
    elements.append(Spacer(1, 0.6*cm))
    elements.append(HRFlowable(width='100%', thickness=1, color=GRIS_BORD))
    elements.append(Spacer(1, 0.2*cm))
    footer_tbl = Table([[
        Paragraph(
            '<font size=8 color="#94a3b8">MLC Technologies Rim — Nouakchott, Mauritanie</font>',
            style('FL')),
        Paragraph(
            '<font size=8 color="#94a3b8">+222 49 71 79 05</font>',
            style('FC')),
        Paragraph(
            f'<font size=8 color="#94a3b8">Devis généré le {devis.date_creation.strftime("%d/%m/%Y")}</font>',
            style('FR')),
    ]], colWidths=[6*cm, 6*cm, 6*cm])
    footer_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
    ]))
    elements.append(footer_tbl)

    doc.build(elements)
    return response

# ════════════════════════════════════════
# API
# ════════════════════════════════════════
def api_produit_prix(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    return JsonResponse({
        'prix_vente': str(produit.prix_vente),
        'nom': produit.nom,
        'reference': produit.reference,
        'stock': produit.quantite_stock,
    })


# ════════════════════════════════════════
# RAPPORTS
# ════════════════════════════════════════
def rapports(request):
    return render(request, 'stock/rapports.html', {
        'total_produits': Produit.objects.count(),
        'total_clients': Client.objects.count(),
        'total_factures': Facture.objects.count(),
    })
    
    
    
def categorie_supprimer(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        categorie.delete()
        messages.success(request, "Catégorie supprimée.")
        return redirect('stock:categorie_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': categorie})




def rapports(request):
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncMonth
    from .models import Vente, Paiement
    import json

    # ── Ventes par mois ──
    ventes_mois = Vente.objects.annotate(
        mois=TruncMonth('date')
    ).values('mois').annotate(
        total=Sum('total')
    ).order_by('mois')[:12]

    labels_ventes = [v['mois'].strftime('%b %Y') if v['mois'] else '' for v in ventes_mois]
    data_ventes   = [float(v['total']) for v in ventes_mois]

    # ── Stock par catégorie ──
    from .models import Categorie
    categories = Categorie.objects.all()
    labels_stock = []
    data_stock   = []
    for cat in categories:
        total = sum(p.quantite_stock for p in cat.produit_set.all())
        if total > 0:
            labels_stock.append(cat.nom)
            data_stock.append(total)

    # ── Modes de paiement ──
    modes = Paiement.objects.values('mode_paiement').annotate(
        total=Sum('montant'), count=Count('id')
    )
    labels_modes = [m['mode_paiement'] for m in modes]
    data_modes   = [float(m['total']) for m in modes]

    # ── Top produits vendus ──
    from .models import LigneVente
    top_produits = LigneVente.objects.values(
        'produit__nom'
    ).annotate(
        total_qte=Sum('quantite'),
        total_ca=Sum('sous_total') if False else Count('id')
    ).order_by('-total_qte')[:5]

    # ── Chiffres clés ──
    total_ca      = Vente.objects.aggregate(Sum('total'))['total__sum'] or 0
    total_factures = Facture.objects.count()
    factures_payees = Facture.objects.filter(statut='payee').count()
    total_clients  = Client.objects.count()

    context = {
        'total_ca':         total_ca,
        'total_factures':   total_factures,
        'factures_payees':  factures_payees,
        'total_clients':    total_clients,
        'labels_ventes':    json.dumps(labels_ventes),
        'data_ventes':      json.dumps(data_ventes),
        'labels_stock':     json.dumps(labels_stock),
        'data_stock':       json.dumps(data_stock),
        'labels_modes':     json.dumps(labels_modes),
        'data_modes':       json.dumps(data_modes),
        'top_produits':     top_produits,
        'produits_alerte':  [p for p in Produit.objects.all() if p.stock_bas],
    }
    return render(request, 'stock/rapports.html', context)




def login_view(request):
    if request.user.is_authenticated:
        return redirect('stock:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Crée le profil si inexistant
            from .models import Profil
            Profil.objects.get_or_create(user=user)
            messages.success(request, f"Bienvenue, {user.first_name or user.username} !")
            return redirect('stock:dashboard')
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")

    return render(request, 'stock/login.html')


def logout_view(request):
    logout(request)
    return redirect('stock:login')


@login_required(login_url='stock:login')
def profil_view(request):
    from .models import Profil
    profil, _ = Profil.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Infos utilisateur
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name  = request.POST.get('last_name', '')
        request.user.email      = request.POST.get('email', '')
        request.user.save()

        # Profil
        profil.telephone = request.POST.get('telephone', '')
        profil.poste     = request.POST.get('poste', '')
        if 'photo' in request.FILES:
            profil.photo = request.FILES['photo']
        profil.save()

        messages.success(request, "Profil mis à jour !")
        return redirect('stock:profil')

    return render(request, 'stock/profil.html', {'profil': profil})







# ════════════════════════════════════════
# INSTALLATIONS
# ════════════════════════════════════════
def installation_liste(request):
    installations = Installation.objects.select_related('client', 'site').order_by('-date_creation')
    return render(request, 'stock/installation_liste.html', {'installations': installations})

def installation_ajouter(request):
    from .forms import InstallationForm
    form = InstallationForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Installation créée !")
        return redirect('stock:installation_liste')
    return render(request, 'stock/installation_form.html', {
        'form':    form,
        'titre':   'Nouvelle installation',
        'clients': Client.objects.all().order_by('nom'),
    })
    
def installation_detail(request, pk):
    installation = get_object_or_404(Installation, pk=pk)
    return render(request, 'stock/installation_detail.html', {'installation': installation})

def installation_modifier(request, pk):
    installation = get_object_or_404(Installation, pk=pk)
    from .forms import InstallationForm
    form = InstallationForm(request.POST or None, instance=installation)
    if form.is_valid():
        form.save()
        messages.success(request, "Installation modifiée !")
        return redirect('stock:installation_detail', pk=pk)
    return render(request, 'stock/installation_form.html', {'form': form, 'titre': 'Modifier installation'})

def installation_supprimer(request, pk):
    installation = get_object_or_404(Installation, pk=pk)
    if request.method == 'POST':
        installation.delete()
        messages.success(request, "Installation supprimée.")
        return redirect('stock:installation_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': installation})


# ════════════════════════════════════════
# MAINTENANCES
# ════════════════════════════════════════
def maintenance_liste(request):
    maintenances = Maintenance.objects.select_related('client', 'site').order_by('-date_creation')
    context = {
        'maintenances':  maintenances,
        'total':         maintenances.count(),
        'nb_ouverts':    maintenances.filter(statut='ouvert').count(),
        'nb_en_cours':   maintenances.filter(statut='en_cours').count(),
        'nb_resolus':    maintenances.filter(statut='resolu').count(),
        'nb_urgents':    maintenances.filter(priorite='urgente').count(),
    }
    return render(request, 'stock/maintenance_liste.html', context)

def maintenance_ajouter(request):
    from .forms import MaintenanceForm
    form = MaintenanceForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Ticket SAV créé !")
        return redirect('stock:maintenance_liste')
    return render(request, 'stock/maintenance_form.html', {
        'form':     form,
        'titre':    'Nouveau ticket SAV',
        'clients':  Client.objects.all().order_by('nom'),
        'sites':    Site.objects.select_related('client').all(),
        'factures': Facture.objects.select_related('client').order_by('-date_creation'),
    })

def maintenance_detail(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    return render(request, 'stock/maintenance_detail.html', {'maintenance': maintenance})

def maintenance_modifier(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    from .forms import MaintenanceForm
    form = MaintenanceForm(request.POST or None, instance=maintenance)
    if form.is_valid():
        form.save()
        messages.success(request, "Ticket modifié !")
        return redirect('stock:maintenance_detail', pk=pk)
    return render(request, 'stock/maintenance_form.html', {
        'form':     form,
        'titre':    'Modifier ticket SAV',
        'clients':  Client.objects.all().order_by('nom'),
        'sites':    Site.objects.select_related('client').all(),
        'factures': Facture.objects.select_related('client').order_by('-date_creation'),
    })

def maintenance_supprimer(request, pk):
    maintenance = get_object_or_404(Maintenance, pk=pk)
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, "Ticket supprimé.")
        return redirect('stock:maintenance_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': maintenance})


# ════════════════════════════════════════
# CONTRATS
# ════════════════════════════════════════
def contrat_liste(request):
    contrats = Contrat.objects.select_related('client').order_by('-date_creation')
    context = {
        'contrats':      contrats,
        'total':         contrats.count(),
        'nb_actifs':     contrats.filter(statut='actif').count(),
        'nb_expires':    contrats.filter(statut='expire').count(),
        'nb_resilies':   contrats.filter(statut='resilie').count(),
        'nb_attente':    contrats.filter(statut='en_attente').count(),
    }
    return render(request, 'stock/contrat_liste.html', context)

def contrat_ajouter(request):
    from .forms import ContratForm
    form = ContratForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Contrat créé !")
        return redirect('stock:contrat_liste')
    return render(request, 'stock/contrat_form.html', {'form': form, 'titre': 'Nouveau contrat'})

def contrat_detail(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk)
    return render(request, 'stock/contrat_detail.html', {'contrat': contrat})

def contrat_modifier(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk)
    from .forms import ContratForm
    form = ContratForm(request.POST or None, instance=contrat)
    if form.is_valid():
        form.save()
        messages.success(request, "Contrat modifié !")
        return redirect('stock:contrat_detail', pk=pk)
    return render(request, 'stock/contrat_form.html', {'form': form, 'titre': 'Modifier contrat'})

def contrat_supprimer(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk)
    if request.method == 'POST':
        contrat.delete()
        messages.success(request, "Contrat supprimé.")
        return redirect('stock:contrat_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': contrat})


# ════════════════════════════════════════
# SITES
# ════════════════════════════════════════

def site_quick(request):
    if request.method == 'POST':
        try:
            nom         = request.POST.get('nom', '').strip()
            client_id   = request.POST.get('client', '').strip()
            adresse     = request.POST.get('adresse', '').strip()
            latitude    = request.POST.get('latitude', '').strip()
            longitude   = request.POST.get('longitude', '').strip()
            description = request.POST.get('description', '').strip()

            if not nom:       return JsonResponse({'success': False, 'errors': 'Nom obligatoire'})
            if not client_id: return JsonResponse({'success': False, 'errors': 'Client obligatoire'})
            if not adresse:   return JsonResponse({'success': False, 'errors': 'Adresse obligatoire'})

            client = get_object_or_404(Client, pk=int(client_id))

            site = Site(
                nom=nom, client=client,
                adresse=adresse, description=description
            )
            if latitude:  site.latitude  = latitude
            if longitude: site.longitude = longitude
            site.save()

            return JsonResponse({
                'success': True,
                'id':      site.pk,
                'nom':     site.nom,
                'client':  site.client.nom,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'errors': str(e)})

    return JsonResponse({'success': False, 'errors': 'Méthode non autorisée'})

def site_liste(request):
    sites = Site.objects.select_related('client').order_by('-date_ajout')
    return render(request, 'stock/site_liste.html', {'sites': sites})

def site_ajouter(request):
    from .forms import SiteForm
    form = SiteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Site ajouté !")
        return redirect('stock:site_liste')
    return render(request, 'stock/site_form.html', {'form': form, 'titre': 'Nouveau site'})

def site_supprimer(request, pk):
    site = get_object_or_404(Site, pk=pk)
    if request.method == 'POST':
        site.delete()
        messages.success(request, "Site supprimé.")
        return redirect('stock:site_liste')
    return render(request, 'stock/confirmer_suppression.html', {'objet': site})



def site_detail(request, pk):
    site = get_object_or_404(Site, pk=pk)
    return render(request, 'stock/site_detail.html', {'site': site})

def site_modifier(request, pk):
    site = get_object_or_404(Site, pk=pk)
    from .forms import SiteForm
    form = SiteForm(request.POST or None, instance=site)
    if form.is_valid():
        form.save()
        messages.success(request, "Site modifié !")
        return redirect('stock:site_detail', pk=pk)
    return render(request, 'stock/site_form.html', {
        'form': form, 'titre': 'Modifier le site'
    })








def installation_quick(request):
    if request.method == 'POST':
        try:
            # Récupère les données
            reference   = request.POST.get('reference', '').strip()
            client_id   = request.POST.get('client', '').strip()
            site_id     = request.POST.get('site', '').strip()
            technicien  = request.POST.get('technicien', '').strip()
            date_prevue = request.POST.get('date_prevue', '').strip()
            date_reelle = request.POST.get('date_reelle', '').strip()
            statut      = request.POST.get('statut', 'planifie').strip()
            facture_id  = request.POST.get('facture', '').strip()
            description = request.POST.get('description', '').strip()
            notes       = request.POST.get('notes', '').strip()

            # Validations
            if not reference:
                return JsonResponse({'success': False, 'errors': 'Référence obligatoire'})
            if not client_id:
                return JsonResponse({'success': False, 'errors': 'Client obligatoire'})
            if not date_prevue:
                return JsonResponse({'success': False, 'errors': 'Date prévue obligatoire'})

            # Vérifie si la référence existe déjà
            if Installation.objects.filter(reference=reference).exists():
                return JsonResponse({'success': False, 'errors': f'La référence {reference} existe déjà'})

            # Récupère les objets liés
            client = get_object_or_404(Client, pk=int(client_id))

            site = None
            if site_id:
                try:
                    site = Site.objects.get(pk=int(site_id))
                except Site.DoesNotExist:
                    pass

            facture = None
            if facture_id:
                try:
                    facture = Facture.objects.get(pk=int(facture_id))
                except Facture.DoesNotExist:
                    pass

            # Crée l'installation
            inst = Installation(
                reference   = reference,
                client      = client,
                site        = site,
                technicien  = technicien,
                date_prevue = date_prevue,
                statut      = statut,
                description = description,
                notes       = notes,
                facture     = facture,
            )

            # Date réelle optionnelle
            if date_reelle:
                inst.date_reelle = date_reelle

            inst.save()

            return JsonResponse({
                'success':   True,
                'id':        inst.pk,
                'reference': inst.reference,
                'client':    inst.client.nom,
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'errors': str(e)})

    return JsonResponse({'success': False, 'errors': 'Méthode non autorisée'})