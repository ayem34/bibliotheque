from django.db import models
from django.contrib.auth.models import AbstractUser

# Si tu veux gérer les utilisateurs avec Django Auth
class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('ADHERENT', 'Adherent'),
        ('ADMIN', 'Administrateur'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Adherent')
    
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username  # ou self.email 

class Auteur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)
    nationalite = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

class TypeLivre(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom

class Editeur(models.Model):
    nom = models.CharField(max_length=100)
    site_web = models.URLField(blank=True)

    def __str__(self):
        return self.nom

class Livre(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.ForeignKey(Auteur, on_delete=models.SET_NULL, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True)
    type_livre = models.ForeignKey(TypeLivre, on_delete=models.SET_NULL, null=True)
    editeur = models.ForeignKey(Editeur, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    fichier_pdf = models.FileField(upload_to='pdfs/', blank=True, null=True)
    est_numerique = models.BooleanField(default=False)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

class Exemplaire(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    code_barre = models.CharField(max_length=30, unique=True)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.livre.titre} - {self.code_barre}"

class Emprunt(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDE', 'Validé'),
        ('RENDU', 'Rendu'),
    ]
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    exemplaire = models.ForeignKey(Exemplaire, on_delete=models.CASCADE)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_retour = models.DateTimeField(blank=True, null=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='EN_ATTENTE')
    
#l utliosateur ne peut laisser qu un seul commentaire par livre 
class Commentaire(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    note = models.IntegerField(default=0)
    contenu = models.TextField(blank=True)
    date_commentaire = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('utilisateur', 'livre')  # <-- limitation unique

class Notification(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    message = models.TextField()
    est_lu = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)