from django.shortcuts import render, redirect,get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import views as auth_views
from django.contrib.auth import get_user_model
from .forms import UtilisateurForm,AuteurForm ,CategorieForm, TypeLivreForm, EditeurForm ,LivreForm,EmpruntForm ,ExemplaireForm ,CommentaireForm ,EmpruntAdherentForm #  créer dans forms.py
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, F, Func,Q

from app_biblio.models import Utilisateur, Emprunt, Commentaire, Auteur, Categorie, TypeLivre, Editeur, Livre, Exemplaire,Commentaire, Notification

from datetime import timedelta
from django.utils import timezone

def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'

def is_adherent(user):
    return user.is_authenticated and user.role == 'ADHERENT'

# Page d'accueil → redirection vers login
def home(request):
    return redirect('login')  # ou 'dashboard' si tu veux aller direct au dashboard

# Dashboard protégé
login_required
def dashboard(request):
    user = request.user

    if user.role == 'ADMIN':
        # --------------------------
        # Statistiques globales admin
        # --------------------------
        total_utilisateurs = Utilisateur.objects.count()
        repartition_roles = Utilisateur.objects.annotate(
            role_upper=Func(F('role'), function='UPPER')
        ).values('role_upper').annotate(total=Count('id'))
        top_emprunteurs = Utilisateur.objects.annotate(
            nb_emprunts=Count('emprunt')
        ).order_by('-nb_emprunts')[:5]
        top_commentateurs = Utilisateur.objects.annotate(
            nb_commentaires=Count('commentaire')
        ).order_by('-nb_commentaires')[:5]

        # Statistiques livres / exemplaires
        total_livres = Livre.objects.count()
        total_exemplaires = Exemplaire.objects.count()
        exemplaires_disponibles = Exemplaire.objects.filter(disponible=True).count()
        exemplaires_empruntes = Exemplaire.objects.filter(disponible=False).count()

        # Statistiques emprunts
        emprunts_en_attente = Emprunt.objects.filter(statut='EN_ATTENTE').count()
        emprunts_valides = Emprunt.objects.filter(statut='VALIDE').count()
        emprunts_rendus = Emprunt.objects.filter(statut='RENDU').count()

        context = {
            'user': user,
            'is_admin': True,
            'total_utilisateurs': total_utilisateurs,
            'repartition_roles': repartition_roles,
            'top_emprunteurs': top_emprunteurs,
            'top_commentateurs': top_commentateurs,
            'total_livres': total_livres,
            'total_exemplaires': total_exemplaires,
            'exemplaires_disponibles': exemplaires_disponibles,
            'exemplaires_empruntes': exemplaires_empruntes,
            'emprunts_en_attente': emprunts_en_attente,
            'emprunts_valides': emprunts_valides,
            'emprunts_rendus': emprunts_rendus,
        }

    else:
        # --------------------------
        # Dashboard adhérent
        # --------------------------
        adherent = user

        # Emprunts en cours (EN_ATTENTE ou VALIDE)
        emprunts_en_cours = Emprunt.objects.filter(
            utilisateur=adherent,
            statut__in=['EN_ATTENTE', 'VALIDE']
        )

        total_emprunts = Emprunt.objects.filter(utilisateur=adherent).count()

        # Livres récents avec le nombre d'exemplaires disponibles
        nouveaux_livres = (
            Livre.objects.annotate(
                nb_disponibles=Count('exemplaire', filter=Q(exemplaire__disponible=True))
            )
            .order_by('-date_ajout')[:3]
        )

        # Vérification de retard pour les emprunts
        now = timezone.now()
        for e in emprunts_en_cours:
            if e.date_retour:
                # Compare datetime directement
                e.est_retard = e.date_retour < now
            else:
                e.est_retard = False

        context = {
            'is_admin': False,
            'emprunts_en_cours': emprunts_en_cours,
            'total_emprunts': total_emprunts,
            'nouveaux_livres': nouveaux_livres,
        }

    return render(request, 'index.html', context)


# Login et logout avec templates SB Admin 2
login_view = auth_views.LoginView.as_view(template_name='login.html',redirect_authenticated_user=True) #redirect_authentificated_user=True si un utlisateur deja connecter tenter vister login il direiger vers login_redirect_url
logout_view = auth_views.LogoutView.as_view()



User = get_user_model()


# Liste des utilisateurs (admin uniquement)
@login_required
@user_passes_test(is_admin)
def liste_utilisateurs(request):
    users = User.objects.all()
    return render(request, 'utilisateurs/liste.html', {'utilisateurs': users})

# Ajouter un utilisateur (admin uniquement)
@login_required
#seul les admin peuve acceder a cet espace 
@user_passes_test(is_admin)
def ajouter_utilisateur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'ADHERENT'  # rôle par défaut
            user.set_password(form.cleaned_data['password1'])  # encode le mot de passe
            user.save()
            messages.success(request, "Utilisateur créé avec succès !") 
            
           # return redirect('liste_utilisateurs')
            return redirect('dashboard')
        else :
            messages.error(request,"veuillez corriger les erreurs du formulaire ")
    else:
        form = UtilisateurForm()
    return render(request, 'utilisateurs/ajouter.html', {'form': form})




@login_required
def liste_livres(request):
    livres = Livre.objects.all()
    return render(request, 'livres/liste.html', {'livres': livres})


#gestion catalogue

#auteur
@login_required
def ajouter_auteur(request):
    if request.method == 'POST':
        form = AuteurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_catalogue')
    else:
        form = AuteurForm()
    return render(request, 'auteur/ajouter.html', {'form': form})

@login_required
def modifier_auteur(request, id):
    auteur = get_object_or_404(Auteur, id=id)
    if request.method == 'POST':
        form = AuteurForm(request.POST, instance=auteur)
        if form.is_valid():
            form.save()
            return redirect('liste_catalogue')  # redirige vers la liste complète
    else:
        form = AuteurForm(instance=auteur)
    return render(request, 'auteur/ajouter.html', {'form': form})


@login_required
def supprimer_auteur(request, id):
    auteur = get_object_or_404(Auteur, id=id)
    auteur.delete()
    return redirect('liste_catalogue')


#categorie
def ajouter_categorie(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_catalogue')  
    else:
        form = CategorieForm()
    return render(request, 'catalogue/ajouter_categorie.html', {'form': form})

@login_required
def modifier_categorie(request, id):
    categorie = get_object_or_404(Categorie, id=id)
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            return redirect('liste_catalogue')
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'catalogue/ajouter_categorie.html', {'form': form})


@login_required
def supprimer_categorie(request, id):
    categorie = get_object_or_404(Categorie, id=id)
    categorie.delete()
    return redirect('liste_catalogue')
#type livre 
def ajouter_type_livre(request):
    if request.method == 'POST':
        form = TypeLivreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_catalogue')
    else:
        form = TypeLivreForm()
    return render(request, 'catalogue/ajouter_type_livre.html', {'form': form})

@login_required
def modifier_type_livre(request, id):
    type_livre = get_object_or_404(TypeLivre, id=id)
    if request.method == 'POST':
        form = TypeLivreForm(request.POST, instance=type_livre)
        if form.is_valid():
            form.save()
            return redirect('liste_catalogue')
    else:
        form = TypeLivreForm(instance=type_livre)
    return render(request, 'catalogue/ajouter_type_livre.html', {'form': form})

@login_required
def supprimer_type_livre(request, id):
    type_livre = get_object_or_404(TypeLivre, id=id)
    type_livre.delete()
    return redirect('liste_catalogue')

#editeur
def ajouter_editeur(request):
    if request.method == 'POST':
        form = EditeurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_catalogue')
    else:
        form = EditeurForm()
    return render(request, 'catalogue/ajouter_editeur.html', {'form': form})

@login_required
def modifier_editeur(request, id):
    editeur = get_object_or_404(Editeur, id=id)
    if request.method == 'POST':
        form = EditeurForm(request.POST, instance=editeur)
        if form.is_valid():
            form.save()
            return redirect('liste_catalogue')
    else:
        form = EditeurForm(instance=editeur)
    return render(request, 'catalogue/ajouter_editeur.html', {'form': form})


@login_required
def supprimer_editeur(request, id):
    editeur = get_object_or_404(Editeur, id=id)
    editeur.delete()
    return redirect('liste_catalogue')


#vue pour ajouter livre 
@login_required
def ajouter_livre(request):
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_livres')  # ou dashboard
    else:
        form = LivreForm()
    return render(request, 'livres/ajouter.html', {'form': form})


@login_required
def liste_catalogue(request):
    auteurs = Auteur.objects.all()
    categories = Categorie.objects.all()
    types_livre = TypeLivre.objects.all()
    editeurs = Editeur.objects.all()
    context = {
        'auteurs': auteurs,
        'categories': categories,
        'types_livre': types_livre,
        'editeurs': editeurs,
    }
    return render(request, 'catalogue/liste.html', context)


#crud sur les livre 

def liste_livres(request):
    livres = Livre.objects.select_related('auteur', 'categorie', 'type_livre', 'editeur').annotate(
        nb_disponibles=Count('exemplaire', filter=Q(exemplaire__disponible=True))
    )


    
     #  filtrer ou chercher :
    query = request.GET.get('q')
    if query:
        livres = livres.filter(titre__icontains=query)


    return render(request, 'livres/liste.html', {
        'livres': livres,
        'role': request.user.role  # On passe le rôle au template
    })


def ajouter_livre(request):
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('liste_livres')
    else:
        form = LivreForm()
    return render(request, 'livres/ajouter.html', {'form': form})



def modifier_livre(request, id):
    livre = get_object_or_404(Livre, id=id)
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES, instance=livre)
        if form.is_valid():
            form.save()
            return redirect('liste_livres')
    else:
        form = LivreForm(instance=livre)
    return render(request, 'livres/ajouter.html', {'form': form, 'livre': livre})

def supprimer_livre(request, id):
    livre = get_object_or_404(Livre, id=id)
    livre.delete()
    return redirect('liste_livres')


# crud sur exemplaire 
def liste_exemplaires(request):
    exemplaires = Exemplaire.objects.all()
    return render(request, 'exemplaires/liste.html', {'exemplaires': exemplaires})

def ajouter_exemplaire(request):
    if request.method == 'POST':
        form = ExemplaireForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_exemplaires')
    else:
        form = ExemplaireForm()
    return render(request, 'exemplaires/ajouter.html', {'form': form})

def modifier_exemplaire(request, id):
    exemplaire = get_object_or_404(Exemplaire, id=id)
    if request.method == 'POST':
        form = ExemplaireForm(request.POST, instance=exemplaire)
        if form.is_valid():
            form.save()
            return redirect('liste_exemplaires')
    else:
        form = ExemplaireForm(instance=exemplaire)
    return render(request, 'exemplaires/modifier.html', {'form': form})

def supprimer_exemplaire(request, id):
    exemplaire = get_object_or_404(Exemplaire, id=id)
    exemplaire.delete()
    return redirect('liste_exemplaires')

#crud sur gestion emprunts 
@login_required
def liste_emprunts(request):
    """
    Affiche :
    - Pour l'admin : tous les emprunts
    - Pour l'adhérent : seulement ses propres emprunts
    """
    if request.user.role.upper() == 'ADMIN':
        emprunts = Emprunt.objects.select_related('utilisateur', 'exemplaire__livre')
    else:
        # L'adhérent ne voit que ses emprunts
        emprunts = Emprunt.objects.select_related('exemplaire__livre').filter(utilisateur=request.user)
    
    return render(request, 'emprunts/liste.html', {'emprunts': emprunts})

def ajouter_emprunt(request):
    if request.method == 'POST':
        form = EmpruntForm(request.POST)
        if form.is_valid():
            emprunt = form.save(commit=False)

            # Vérifie si l'utilisateur a déjà un emprunt actif
            emprunt_actif = Emprunt.objects.filter(
                utilisateur=emprunt.utilisateur,
                statut__in=['EN_ATTENTE', 'VALIDE']
            ).exists()
            if emprunt_actif:
                form.add_error(None, "L'utilisateur a déjà un emprunt en cours.")
            elif not emprunt.exemplaire.disponible:
                form.add_error('exemplaire', "Cet exemplaire est déjà emprunté.")
            else:
                emprunt.save()
                emprunt.exemplaire.disponible = False
                emprunt.exemplaire.save()
                return redirect('liste_emprunts')
    else:
        form = EmpruntForm()
    return render(request, 'emprunts/ajouter.html', {'form': form})
def modifier_emprunt(request, id):
    emprunt = get_object_or_404(Emprunt, id=id)
    if request.method == 'POST':
        form = EmpruntForm(request.POST, instance=emprunt)
        if form.is_valid():
            form.save()
            return redirect('liste_emprunts')
    else:
        form = EmpruntForm(instance=emprunt)
    return render(request, 'emprunts/ajouter.html', {'form': form, 'emprunt': emprunt})

def supprimer_emprunt(request, id):
    emprunt = get_object_or_404(Emprunt, id=id)
    exemplaire = emprunt.exemplaire
    emprunt.delete()
    # Si supprimé, on rend l’exemplaire à nouveau disponible
    exemplaire.disponible = True
    exemplaire.save()
    return redirect('liste_emprunts')
#gestion emprunt cote adherent 
@login_required
def demander_emprunt(request):
    if request.method == 'POST':
        form = EmpruntAdherentForm(request.POST)
        if form.is_valid():
            # Vérifier si l'utilisateur a déjà un emprunt actif
            emprunt_actif = Emprunt.objects.filter(
                utilisateur=request.user,
                statut__in=['EN_ATTENTE', 'VALIDE']
            ).exists()
            if emprunt_actif:
                form.add_error(None, "Vous avez déjà un emprunt en cours.")
            else:
                emprunt = form.save(commit=False)
                emprunt.utilisateur = request.user
                emprunt.statut = 'EN_ATTENTE'
                emprunt.date_retour = timezone.now() + timedelta(days=7)
                emprunt.save()
                emprunt.exemplaire.disponible = False
                emprunt.exemplaire.save()
                return redirect('mes_emprunts')
    else:
        form = EmpruntAdherentForm()

    return render(request, 'emprunts/demander.html', {'form': form})
@login_required
def detail_livre(request, id):
    livre = get_object_or_404(Livre, id=id)

    # Récupérer le commentaire de l'utilisateur s'il existe
    commentaire_utilisateur = Commentaire.objects.filter(livre=livre, utilisateur=request.user).first()
    deja_commente = bool(commentaire_utilisateur)

    form = None
    en_modification = False

    if request.user.is_authenticated and request.user.role.upper() == 'ADHERENT':
        if request.method == 'POST':
            # AJOUT
            if 'ajouter_commentaire' in request.POST and not deja_commente:
                form = CommentaireForm(request.POST)
                if form.is_valid():
                    c = form.save(commit=False)
                    c.livre = livre
                    c.utilisateur = request.user
                    c.save()
                    # Notification uniquement pour l'ajout
                    for admin in Utilisateur.objects.filter(role__iexact='ADMIN'):
                        Notification.objects.create(
                            utilisateur=admin,
                            message=f"Nouveau commentaire sur « {livre.titre} » par {request.user.username}."
                        )
                    return redirect('detail_livre', id=livre.id)

            # DEMANDER MODIFICATION
            elif 'demander_modification' in request.POST and deja_commente:
                en_modification = True
                form = CommentaireForm(instance=commentaire_utilisateur)

            # VALIDER MODIFICATION
            elif 'modifier_commentaire' in request.POST and deja_commente:
                form = CommentaireForm(request.POST, instance=commentaire_utilisateur)
                if form.is_valid():
                    form.save()
                    # Pas de notification pour modification
                    return redirect('detail_livre', id=livre.id)

            # ANNULER MODIFICATION
            elif 'annuler_modification' in request.POST:
                return redirect('detail_livre', id=livre.id)

            # SUPPRESSION
            elif 'supprimer_commentaire' in request.POST and deja_commente:
                commentaire_utilisateur.delete()
                # Notification pour suppression
                for admin in Utilisateur.objects.filter(role__iexact='ADMIN'):
                    Notification.objects.create(
                        utilisateur=admin,
                        message=f"Commentaire supprimé sur « {livre.titre} » par {request.user.username}."
                    )
                return redirect('detail_livre', id=livre.id)

        # Préparer le formulaire
        if deja_commente and not en_modification:
            form = None
        elif deja_commente and en_modification:
            form = CommentaireForm(instance=commentaire_utilisateur)
        else:
            form = CommentaireForm()

    # Pagination des commentaires
    commentaires_qs = Commentaire.objects.filter(livre=livre).order_by('-date_commentaire')
    paginator = Paginator(commentaires_qs, 5)  # 5 commentaires par page
    page_number = request.GET.get('page')
    commentaires = paginator.get_page(page_number)

    return render(request, 'livres/detail_livre.html', {
        'livre': livre,
        'commentaires': commentaires,
        'form': form,
        'deja_commente': deja_commente,
        'commentaire_utilisateur': commentaire_utilisateur,
        'en_modification': en_modification,
    })

@login_required
def mes_notifications(request):
    """Notifications pour l'utilisateur connecté"""
    notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date_envoi')
    return render(request, 'notifications/liste_notifications.html', {'notifications': notifications})

def liste_notifications(request):
    """Afficher toutes les notifications pour l'admin ou les siennes pour un utilisateur"""
    if request.user.role.upper() == 'ADMIN':
        notifications = Notification.objects.all().order_by('-date_envoi')
    else:
        notifications = Notification.objects.filter(utilisateur=request.user).order_by('-date_envoi')
    return render(request, 'notifications/liste_notifications.html', {'notifications': notifications})

def marquer_lu(request, notif_id):
    """Marquer une notification comme lue"""
    notif = get_object_or_404(Notification, id=notif_id, utilisateur=request.user)
    notif.est_lu = True
    notif.save()
    #return redirect('liste_notifications')  
    # Redirige vers le dashboard au lieu de liste_notifications
    return redirect('dashboard')  

def marquer_toutes_lues(request):
    """Marquer toutes les notifications comme lues pour l'utilisateur ou l'admin"""
    if request.user.is_authenticated:
        if request.user.role.upper() == 'ADMIN':
            Notification.objects.all().update(est_lu=True)
        else:
            Notification.objects.filter(utilisateur=request.user).update(est_lu=True)
    return redirect('liste_notifications')

@login_required
def liste_commentaires(request):
    livre_id = request.GET.get('livre_id')
    livres = Livre.objects.all()  # nécessaire pour le filtre admin

    if request.user.role == 'ADMIN':
        commentaires = Commentaire.objects.all().order_by('-date_commentaire')
        if livre_id:
            commentaires = commentaires.filter(livre__id=livre_id)
    else:
        commentaires = Commentaire.objects.filter(utilisateur=request.user).order_by('-date_commentaire')
        if livre_id:
            commentaires = commentaires.filter(livre__id=livre_id)

    return render(request, 'commentaires/liste_commentaires.html', {
        'commentaires': commentaires,
        'role': request.user.role,  
        'livres': livres
    })



