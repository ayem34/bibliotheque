from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'), #route racie pour /
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # --- Gestion des utilisateurs ---
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/ajouter/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    

    # --- Gestion catalogue ---#

    # --- Gestion des catégories ---
    path('categorie/modifier/<int:id>/', views.modifier_categorie, name='modifier_categorie'),
    path('categorie/supprimer/<int:id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('ajouter-categorie/', views.ajouter_categorie, name='ajouter_categorie'),
     # --- Gestion des types de livres ---
    path('type-livre/modifier/<int:id>/', views.modifier_type_livre, name='modifier_type_livre'),
    path('type-livre/supprimer/<int:id>/', views.supprimer_type_livre, name='supprimer_type_livre'),
    path('ajouter-type-livre/', views.ajouter_type_livre, name='ajouter_type_livre'),

   
    # --- Gestion des éditeurs ---
    path('editeur/modifier/<int:id>/', views.modifier_editeur, name='modifier_editeur'),
    path('editeur/supprimer/<int:id>/', views.supprimer_editeur, name='supprimer_editeur'),
    path('ajouter-editeur/', views.ajouter_editeur, name='ajouter_editeur'),

    path('catalogue/', views.liste_catalogue, name='liste_catalogue'),
    path('ajouter-auteur/', views.ajouter_auteur, name='ajouter_auteur'),
    path('auteur/modifier/<int:id>/', views.modifier_auteur, name='modifier_auteur'),
    path('auteur/supprimer/<int:id>/', views.supprimer_auteur, name='supprimer_auteur'),
   

   # ---Gestion livre ---#
   path('livres/', views.liste_livres, name='liste_livres'),
   path('livres/ajouter/', views.ajouter_livre, name='ajouter_livre'),
   path('livres/modifier/<int:id>/', views.modifier_livre, name='modifier_livre'),
   path('livres/supprimer/<int:id>/', views.supprimer_livre, name='supprimer_livre'),

# ---Gestion emplaires  ---#
   path('exemplaires/', views.liste_exemplaires, name='liste_exemplaires'),
   path('exemplaires/ajouter/', views.ajouter_exemplaire, name='ajouter_exemplaire'),
   path('exemplaires/modifier/<int:id>/', views.modifier_exemplaire, name='modifier_exemplaire'),
   path('exemplaires/supprimer/<int:id>/', views.supprimer_exemplaire, name='supprimer_exemplaire'),

  # ---Gestion emprunts ---#
  path('emprunts/', views.liste_emprunts, name='liste_emprunts'),
  path('emprunts/ajouter/', views.ajouter_emprunt, name='ajouter_emprunt'),
  path('emprunts/modifier/<int:id>/', views.modifier_emprunt, name='modifier_emprunt'),
  path('emprunts/supprimer/<int:id>/', views.supprimer_emprunt, name='supprimer_emprunt'),

  
  # Demander un nouvel emprunt cote aderhent 
    path('emprunts/demander/', views.demander_emprunt, name='demander_emprunt'),


   # ... tes autres routes ...
    path('livre/<int:id>/', views.detail_livre, name='detail_livre'),
    path('notifications/', views.mes_notifications, name='mes_notifications'),  # Pour voir ses notifications
    path('notifications/liste/', views.liste_notifications, name='liste_notifications'),  # Pour admin ou liste complète 
    path('notifications/lu/<int:notif_id>/', views.marquer_lu, name='marquer_lu'),
    path('notifications/marquer_toutes/', views.marquer_toutes_lues, name='marquer_toutes_lues'),
    path('commentaires/', views.liste_commentaires, name='liste_commentaires'),

]


