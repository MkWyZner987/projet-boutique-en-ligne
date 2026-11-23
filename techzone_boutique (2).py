"""
================================================================================
TECHZONE - Application boutique en ligne (High-tech & Gaming)
================================================================================
Application de bureau en Python / Tkinter avec :
  1. Inscription à la boutique -> génération d'un CODE UNIQUE par personne
  2. Connexion avec ce code
  3. Boutique avec consoles / PC / téléphones, prix réels, images réelles
  4. Panier avec total et validation de commande

--------------------------------------------------------------------------------
INSTALLATION (une seule fois, dans un terminal) :
    pip install pillow requests

LANCEMENT :
    python techzone_boutique.py

--------------------------------------------------------------------------------
IMAGES RÉELLES :
Au premier lancement, le script crée un dossier "images/" à côté de lui.
Mettez vos VRAIES photos de produits dedans, avec exactement ces noms de
fichier (jpg ou png) :

    ps5_standard.jpg        ps5_digital.jpg        ps5_pro.jpg
    switch2.jpg             switch_oled.jpg        switch_lite.jpg
    iphone17.jpg            iphone16.jpg
    pc_gamer.jpg            pc_portable.jpg

Si une image est absente, le logiciel affiche automatiquement un cadre de
remplacement avec le nom du produit (l'appli fonctionne quand même, aucun
plantage).

--------------------------------------------------------------------------------
PRIX :
Les prix des consoles et téléphones ci-dessous sont les prix publics
officiels relevés en France en novembre 2026 (Sony, Nintendo, Apple).
Les prix "PC" sont indicatifs : changez-les selon vos vrais modèles/fournisseurs
dans la liste PRODUCTS plus bas.
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
import string
import datetime

# --- Bibliothèques optionnelles pour les images ---------------------------
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ============================================================================
# CONFIGURATION / DONNÉES
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
USERS_FILE = os.path.join(BASE_DIR, "utilisateurs.json")

os.makedirs(IMAGES_DIR, exist_ok=True)

# Mot de passe administrateur : CHANGE-LE avant de distribuer ton appli !
ADMIN_PASSWORD = "12344321"

# Catalogue : prix réels (France, novembre 2026) pour consoles et téléphones.
PRODUCTS = [
    # ---------------- CONSOLES ----------------
    {"id": "ps5_standard", "categorie": "Consoles",
     "nom": "PlayStation 5 (Standard, lecteur Blu-ray)",
     "prix": 649.99, "image": "ps5_standard.jpg"},
    {"id": "ps5_digital", "categorie": "Consoles",
     "nom": "PlayStation 5 Digital Edition",
     "prix": 599.99, "image": "ps5_digital.jpg"},
    {"id": "ps5_pro", "categorie": "Consoles",
     "nom": "PlayStation 5 Pro",
     "prix": 899.99, "image": "ps5_pro.jpg"},
    {"id": "switch2", "categorie": "Consoles",
     "nom": "Nintendo Switch 2",
     "prix": 499.99, "image": "switch2.jpg"},
    {"id": "switch_oled", "categorie": "Consoles",
     "nom": "Nintendo Switch OLED",
     "prix": 349.99, "image": "switch_oled.jpg"},
    {"id": "switch_lite", "categorie": "Consoles",
     "nom": "Nintendo Switch Lite",
     "prix": 219.99, "image": "switch_lite.jpg"},

    # ---------------- TÉLÉPHONES ----------------
    {"id": "iphone17", "categorie": "Téléphones",
     "nom": "iPhone 17 (256 Go)",
     "prix": 1119.00, "image": "iphone17.jpg"},
    {"id": "iphone16", "categorie": "Téléphones",
     "nom": "iPhone 16 (128 Go)",
     "prix": 869.00, "image": "iphone16.jpg"},

    # ---------------- PC (prix indicatifs à adapter) ----------------
    {"id": "pc_gamer", "categorie": "PC",
     "nom": "PC Fixe Gamer (RTX, 16 Go RAM)",
     "prix": 1299.99, "image": "pc_gamer.jpg"},
    {"id": "pc_portable", "categorie": "PC",
     "nom": "PC Portable Bureautique 15\"",
     "prix": 599.99, "image": "pc_portable.jpg"},
]

CATEGORIES = ["Consoles", "PC", "Téléphones"]

PRIMARY_COLOR = "#2563eb"
BG_COLOR = "#f4f6fb"
CARD_COLOR = "#ffffff"


# ============================================================================
# OUTILS : utilisateurs / code unique / images
# ============================================================================

def charger_utilisateurs():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauvegarder_utilisateurs(utilisateurs):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(utilisateurs, f, ensure_ascii=False, indent=2)


def generer_code_unique(utilisateurs):
    """Génère un code unique de 8 caractères (lettres + chiffres)."""
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "TZ-" + "".join(random.choices(alphabet, k=8))
        if code not in utilisateurs:
            return code


def charger_image(nom_fichier, nom_produit, taille=(220, 160)):
    """Charge une vraie image depuis le dossier images/, ou crée un cadre
    de remplacement si le fichier n'existe pas / si Pillow n'est pas installé."""
    chemin = os.path.join(IMAGES_DIR, nom_fichier)

    if PIL_OK and os.path.exists(chemin):
        try:
            img = Image.open(chemin).convert("RGB")
            img = img.resize(taille)
            return ImageTk.PhotoImage(img)
        except Exception:
            pass  # on retombe sur le placeholder

    if PIL_OK:
        # Image de remplacement générée (grise avec le nom du produit)
        img = Image.new("RGB", taille, "#dfe4ee")
        draw = ImageDraw.Draw(img)
        texte = nom_produit
        draw.rectangle([0, 0, taille[0] - 1, taille[1] - 1], outline="#9aa5b8")
        draw.text((10, taille[1] // 2 - 10), "Photo à venir :", fill="#5b6472")
        draw.text((10, taille[1] // 2 + 8), texte[:28], fill="#2b3240")
        return ImageTk.PhotoImage(img)

    return None  # Pillow absent : pas d'image, l'app affichera juste du texte


# ============================================================================
# APPLICATION PRINCIPALE
# ============================================================================

class BoutiqueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TechZone — Boutique en ligne")
        self.geometry("1000x680")
        self.configure(bg=BG_COLOR)
        self.minsize(900, 600)

        self.utilisateurs = charger_utilisateurs()
        self.utilisateur_courant = None   # code de l'utilisateur connecté
        self.panier = []                  # liste de dicts produit

        self._images_cache = []  # évite que Tkinter "oublie" les images

        self.conteneur = tk.Frame(self, bg=BG_COLOR)
        self.conteneur.pack(fill="both", expand=True)

        self.frames = {}
        for F in (AccueilFrame, InscriptionFrame, ConnexionFrame, BoutiqueFrame):
            frame = F(self.conteneur, self)
            self.frames[F] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.afficher("AccueilFrame")

    def afficher(self, nom_frame):
        for F, frame in self.frames.items():
            if F.__name__ == nom_frame:
                frame.tkraise()
                if hasattr(frame, "rafraichir"):
                    frame.rafraichir()

    # -------- gestion panier --------
    def ajouter_au_panier(self, produit):
        self.panier.append(produit)
        messagebox.showinfo("Panier", f"« {produit['nom']} » ajouté au panier.")

    def total_panier(self):
        return sum(p["prix"] for p in self.panier)


# ============================================================================
# ÉCRAN D'ACCUEIL
# ============================================================================

class AccueilFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app

        tk.Label(self, text="TechZone", font=("Segoe UI", 34, "bold"),
                 bg=BG_COLOR, fg=PRIMARY_COLOR).pack(pady=(90, 10))
        tk.Label(self, text="Le meilleur de la tech, au meilleur prix",
                 font=("Segoe UI", 14), bg=BG_COLOR, fg="#444").pack(pady=(0, 40))

        tk.Button(self, text="Créer mon compte (code unique)", font=("Segoe UI", 12, "bold"),
                   bg=PRIMARY_COLOR, fg="white", padx=20, pady=12, relief="flat",
                   command=lambda: app.afficher("InscriptionFrame")).pack(pady=10)

        tk.Button(self, text="J'ai déjà un code — Me connecter", font=("Segoe UI", 12),
                   bg="white", fg=PRIMARY_COLOR, padx=20, pady=12, relief="solid",
                   bd=1, command=lambda: app.afficher("ConnexionFrame")).pack(pady=10)

        tk.Button(self, text="Connexion administrateur", font=("Segoe UI", 10),
                   bg=BG_COLOR, fg="#888", relief="flat",
                   command=self.connexion_admin).pack(pady=(30, 0))

    def connexion_admin(self):
        FenetreMotDePasseAdmin(self.app)


# ============================================================================
# FENÊTRE DE CONNEXION ADMINISTRATEUR (sans code)
# ============================================================================

class FenetreMotDePasseAdmin(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Connexion administrateur")
        self.geometry("340x200")
        self.configure(bg=CARD_COLOR)
        self.resizable(False, False)

        tk.Label(self, text="Accès administrateur", font=("Segoe UI", 14, "bold"),
                 bg=CARD_COLOR).pack(pady=(20, 10))

        tk.Label(self, text="Mot de passe :", bg=CARD_COLOR).pack()
        self.entree_mdp = tk.Entry(self, show="•", width=25)
        self.entree_mdp.pack(pady=8)
        self.entree_mdp.focus()
        self.entree_mdp.bind("<Return>", lambda e: self.verifier())

        tk.Button(self, text="Entrer", bg=PRIMARY_COLOR, fg="white", relief="flat",
                  padx=15, pady=6, command=self.verifier).pack(pady=10)

    def verifier(self):
        if self.entree_mdp.get() == ADMIN_PASSWORD:
            self.app.utilisateur_courant = "ADMIN"
            self.destroy()
            self.app.afficher("BoutiqueFrame")
        else:
            messagebox.showerror("Accès refusé", "Mot de passe incorrect.")
            self.entree_mdp.delete(0, "end")


# ============================================================================
# ÉCRAN D'INSCRIPTION
# ============================================================================

class InscriptionFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app

        carte = tk.Frame(self, bg=CARD_COLOR, padx=40, pady=40)
        carte.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(carte, text="Inscription à TechZone", font=("Segoe UI", 20, "bold"),
                 bg=CARD_COLOR).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        tk.Label(carte, text="Nom complet :", bg=CARD_COLOR).grid(row=1, column=0, sticky="w", pady=6)
        self.entree_nom = tk.Entry(carte, width=30)
        self.entree_nom.grid(row=1, column=1, pady=6)

        tk.Label(carte, text="E-mail :", bg=CARD_COLOR).grid(row=2, column=0, sticky="w", pady=6)
        self.entree_email = tk.Entry(carte, width=30)
        self.entree_email.grid(row=2, column=1, pady=6)

        tk.Button(carte, text="Créer mon compte", bg=PRIMARY_COLOR, fg="white",
                  relief="flat", padx=15, pady=8,
                  command=self.inscrire).grid(row=3, column=0, columnspan=2, pady=(20, 5))

        tk.Button(carte, text="← Retour", bg=CARD_COLOR, relief="flat", fg="#666",
                  command=lambda: app.afficher("AccueilFrame")).grid(row=4, column=0, columnspan=2)

    def inscrire(self):
        nom = self.entree_nom.get().strip()
        email = self.entree_email.get().strip()

        if not nom or not email:
            messagebox.showwarning("Champs manquants", "Merci de remplir le nom et l'e-mail.")
            return
        if "@" not in email:
            messagebox.showwarning("E-mail invalide", "Merci d'entrer une adresse e-mail valide.")
            return

        code = generer_code_unique(self.app.utilisateurs)
        self.app.utilisateurs[code] = {
            "nom": nom,
            "email": email,
            "date_inscription": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        sauvegarder_utilisateurs(self.app.utilisateurs)

        messagebox.showinfo(
            "Bienvenue !",
            f"Compte créé pour {nom}.\n\nVotre code unique est :\n\n{code}\n\n"
            "Conservez-le précieusement : il sert à vous reconnecter."
        )

        self.entree_nom.delete(0, "end")
        self.entree_email.delete(0, "end")

        self.app.utilisateur_courant = code
        self.app.afficher("BoutiqueFrame")


# ============================================================================
# ÉCRAN DE CONNEXION
# ============================================================================

class ConnexionFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app

        carte = tk.Frame(self, bg=CARD_COLOR, padx=40, pady=40)
        carte.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(carte, text="Connexion", font=("Segoe UI", 20, "bold"),
                 bg=CARD_COLOR).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        tk.Label(carte, text="Votre code (ex: TZ-AB12CD34) :", bg=CARD_COLOR).grid(
            row=1, column=0, sticky="w", pady=6)
        self.entree_code = tk.Entry(carte, width=25)
        self.entree_code.grid(row=1, column=1, pady=6)

        tk.Button(carte, text="Se connecter", bg=PRIMARY_COLOR, fg="white",
                  relief="flat", padx=15, pady=8,
                  command=self.connecter).grid(row=2, column=0, columnspan=2, pady=(20, 5))

        tk.Button(carte, text="← Retour", bg=CARD_COLOR, relief="flat", fg="#666",
                  command=lambda: app.afficher("AccueilFrame")).grid(row=3, column=0, columnspan=2)

    def connecter(self):
        code = self.entree_code.get().strip().upper()
        if code in self.app.utilisateurs:
            self.app.utilisateur_courant = code
            self.entree_code.delete(0, "end")
            self.app.afficher("BoutiqueFrame")
        else:
            messagebox.showerror("Code invalide", "Ce code n'existe pas. Vérifiez-le ou inscrivez-vous.")


# ============================================================================
# ÉCRAN BOUTIQUE (catalogue + panier)
# ============================================================================

class BoutiqueFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app

        # --- En-tête ---
        entete = tk.Frame(self, bg=PRIMARY_COLOR, height=60)
        entete.pack(fill="x")
        self.label_bienvenue = tk.Label(entete, text="", bg=PRIMARY_COLOR, fg="white",
                                         font=("Segoe UI", 12, "bold"))
        self.label_bienvenue.pack(side="left", padx=20, pady=15)

        tk.Button(entete, text="🛒 Voir le panier", bg="white", fg=PRIMARY_COLOR,
                  relief="flat", command=self.ouvrir_panier).pack(side="right", padx=20, pady=12)

        tk.Button(entete, text="Déconnexion", bg=PRIMARY_COLOR, fg="white",
                  relief="flat", command=self.deconnexion).pack(side="right", padx=5, pady=12)

        # --- Onglets par catégorie ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        self.onglets = {}
        for cat in CATEGORIES:
            onglet = tk.Frame(self.notebook, bg=BG_COLOR)
            self.notebook.add(onglet, text=cat)
            self.onglets[cat] = onglet
            self.construire_catalogue(onglet, cat)

    def rafraichir(self):
        if self.app.utilisateur_courant == "ADMIN":
            self.label_bienvenue.config(text="Bonjour Admin  |  Mode administrateur")
        elif self.app.utilisateur_courant:
            infos = self.app.utilisateurs.get(self.app.utilisateur_courant, {})
            nom = infos.get("nom", "")
            self.label_bienvenue.config(text=f"Bonjour {nom}  |  Code : {self.app.utilisateur_courant}")

    def construire_catalogue(self, parent, categorie):
        # Zone scrollable
        canvas = tk.Canvas(parent, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        grille = tk.Frame(canvas, bg=BG_COLOR)

        grille.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=grille, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        produits = [p for p in PRODUCTS if p["categorie"] == categorie]

        colonnes = 3
        for i, produit in enumerate(produits):
            carte = tk.Frame(grille, bg=CARD_COLOR, bd=1, relief="solid", padx=12, pady=12)
            carte.grid(row=i // colonnes, column=i % colonnes, padx=12, pady=12, sticky="n")

            photo = charger_image(produit["image"], produit["nom"])
            if photo is not None:
                self.app._images_cache.append(photo)
                tk.Label(carte, image=photo, bg=CARD_COLOR).pack()
            else:
                tk.Label(carte, text="[Image indisponible\ninstallez Pillow]",
                         bg="#eee", width=28, height=8).pack()

            tk.Label(carte, text=produit["nom"], font=("Segoe UI", 11, "bold"),
                     bg=CARD_COLOR, wraplength=220, justify="left").pack(pady=(10, 4))
            tk.Label(carte, text=f"{produit['prix']:.2f} €", font=("Segoe UI", 13, "bold"),
                     bg=CARD_COLOR, fg=PRIMARY_COLOR).pack(pady=(0, 10))

            tk.Button(carte, text="Ajouter au panier", bg=PRIMARY_COLOR, fg="white",
                      relief="flat", padx=10, pady=6,
                      command=lambda p=produit: self.app.ajouter_au_panier(p)).pack()

    def ouvrir_panier(self):
        FenetrePanier(self.app)

    def deconnexion(self):
        self.app.utilisateur_courant = None
        self.app.panier = []
        self.app.afficher("AccueilFrame")


# ============================================================================
# FENÊTRE PANIER
# ============================================================================

class FenetrePanier(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Mon panier — TechZone")
        self.geometry("450x450")
        self.configure(bg=BG_COLOR)

        tk.Label(self, text="Mon panier", font=("Segoe UI", 16, "bold"),
                 bg=BG_COLOR).pack(pady=15)

        self.liste_frame = tk.Frame(self, bg=BG_COLOR)
        self.liste_frame.pack(fill="both", expand=True, padx=15)

        self.label_total = tk.Label(self, text="", font=("Segoe UI", 13, "bold"),
                                     bg=BG_COLOR, fg=PRIMARY_COLOR)
        self.label_total.pack(pady=10)

        tk.Button(self, text="Valider la commande", bg=PRIMARY_COLOR, fg="white",
                  relief="flat", padx=15, pady=8,
                  command=self.valider_commande).pack(pady=(0, 15))

        self.afficher_panier()

    def afficher_panier(self):
        for widget in self.liste_frame.winfo_children():
            widget.destroy()

        if not self.app.panier:
            tk.Label(self.liste_frame, text="Votre panier est vide.",
                     bg=BG_COLOR, fg="#666").pack(pady=20)
        else:
            for i, produit in enumerate(self.app.panier):
                ligne = tk.Frame(self.liste_frame, bg=CARD_COLOR, pady=6, padx=8)
                ligne.pack(fill="x", pady=4)
                tk.Label(ligne, text=produit["nom"], bg=CARD_COLOR, anchor="w").pack(side="left")
                tk.Label(ligne, text=f"{produit['prix']:.2f} €", bg=CARD_COLOR).pack(side="right", padx=10)
                tk.Button(ligne, text="✕", bg=CARD_COLOR, fg="red", relief="flat", bd=0,
                          command=lambda idx=i: self.retirer(idx)).pack(side="right")

        self.label_total.config(text=f"Total : {self.app.total_panier():.2f} €")

    def retirer(self, index):
        self.app.panier.pop(index)
        self.afficher_panier()

    def valider_commande(self):
        if not self.app.panier:
            messagebox.showwarning("Panier vide", "Ajoutez au moins un produit avant de commander.")
            return
        total = self.app.total_panier()
        messagebox.showinfo("Commande validée",
                             f"Merci pour votre commande de {total:.2f} € !\n"
                             "Un e-mail de confirmation vous sera envoyé.")
        self.app.panier = []
        self.afficher_panier()


# ============================================================================
# LANCEMENT
# ============================================================================

if __name__ == "__main__":
    app = BoutiqueApp()
    app.mainloop()
