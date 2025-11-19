from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from .models import Livre
from .models import Auteur,Categorie,TypeLivre,Editeur,Livre,Emprunt,Exemplaire,Commentaire
from django.db.models import Q

User = get_user_model()

class UtilisateurForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}),
        required=True
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data
    

class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = ['titre', 'auteur', 'categorie', 'type_livre', 'editeur', 'description', 'fichier_pdf', 'est_numerique']


class AuteurForm(forms.ModelForm):
    class Meta:
        model = Auteur
        fields = ['nom', 'prenom', 'nationalite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'nationalite': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']

class TypeLivreForm(forms.ModelForm):
    class Meta:
        model = TypeLivre
        fields = ['nom']

class EditeurForm(forms.ModelForm):
    class Meta:
        model = Editeur
        fields = ['nom', 'site_web']
    

class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = ['titre', 'auteur', 'categorie', 'type_livre', 'editeur', 'description', 'fichier_pdf', 'est_numerique']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du livre'}),
            'auteur': forms.Select(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'type_livre': forms.Select(attrs={'class': 'form-control'}),
            'editeur': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Résumé ou description'}),
            'fichier_pdf': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'est_numerique': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

   # def __init__(self, *args, **kwargs):
 #       super().__init__(*args, **kwargs)
## Masquer le champ PDF si est_numerique n'est pas coché
   #     if not (self.data.get('est_numerique') or (self.instance and self.instance.est_numerique)):
  #          self.fields['fichier_pdf'].widget = forms.HiddenInput()

class ExemplaireForm(forms.ModelForm):
    class Meta:
        model = Exemplaire
        fields = ['livre', 'code_barre', 'disponible']
        widgets = {
            'livre': forms.Select(attrs={'class': 'form-control'}),
            'code_barre': forms.TextInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        error_messages = {
            'code_barre': {
                'unique': "Un exemplaire avec ce code barre existe déjà."
            }
        }

class EmpruntForm(forms.ModelForm):
    class Meta:
        model = Emprunt
        fields = ['utilisateur', 'exemplaire', 'statut', 'date_retour']
        widgets = {
            'utilisateur': forms.Select(attrs={'class': 'form-control'}),
            'exemplaire': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'date_retour': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Empêcher de sélectionner un exemplaire déjà emprunté
        emprunt_occupe = Emprunt.objects.filter(
            Q(statut='EN_ATTENTE') | Q(statut='VALIDE')
        ).values_list('exemplaire_id', flat=True)
        emprunt_occupe = list(emprunt_occupe)

        # Retirer l'exemplaire actuel si modification
        if self.instance and self.instance.pk and self.instance.exemplaire:
            if self.instance.exemplaire.id in emprunt_occupe:
                emprunt_occupe.remove(self.instance.exemplaire.id)

        self.fields['exemplaire'].queryset = Exemplaire.objects.exclude(id__in=emprunt_occupe)

    def clean(self):
        cleaned_data = super().clean()
        date_retour = cleaned_data.get('date_retour')
        date_demande = self.instance.date_demande if self.instance.pk else timezone.now()

        if date_retour and date_retour <= date_demande:
            self.add_error('date_retour', "La date de retour doit être après la date de demande.")

        limite_max = date_demande + timedelta(days=30)
        if date_retour and date_retour > limite_max:
            self.add_error('date_retour', "La date de retour ne peut pas dépasser 30 jours après la date de demande.")

        return cleaned_data
    
    def clean_utilisateur(self):
        utilisateur = self.cleaned_data.get('utilisateur')
        if utilisateur.role.upper() == 'ADMIN':
            raise forms.ValidationError("Un administrateur ne peut pas emprunter de livre.")
        return utilisateur


class EmpruntAdherentForm(forms.ModelForm):
    class Meta:
        model = Emprunt
        fields = ['exemplaire']  # Seul le choix possible pour l'adhérent
        widgets = {
            'exemplaire': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclure les exemplaires déjà empruntés
        emprunt_occupe = Emprunt.objects.filter(
            statut__in=['EN_ATTENTE', 'VALIDE']
        ).values_list('exemplaire_id', flat=True)
        self.fields['exemplaire'].queryset = Exemplaire.objects.exclude(id__in=emprunt_occupe)
        
class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['note', 'contenu']
        widgets = {
            'note': forms.NumberInput(attrs={'min': 0, 'max': 5, 'class': 'form-control'}),
            'contenu': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }