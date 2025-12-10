import os

# Dossiers de stockage des mails
BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
INBOX_DIR = os.path.join(BASE_DATA_DIR, "inbox")
SENT_DIR = os.path.join(BASE_DATA_DIR, "sent")

# Création des dossiers (si pas encore créer)
os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(SENT_DIR, exist_ok=True)


def sauvegarder_mail(destinataire: str, expediteur: str, lignes_message: list[str]) -> None:
    """
    Sauvegarde le mail dans la boîte de réception du destinataire
    sous forme d'un simple fichier texte.
    """
    chemin_fichier = os.path.join(INBOX_DIR, f"{destinataire}.txt")

    with open(chemin_fichier, "a", encoding="utf-8") as f:
        f.write(f"FROM: {expediteur}\n")
        f.write(f"TO: {destinataire}\n")
        f.write("----- MESSAGE -----\n")
        for ligne in lignes_message:
            f.write(ligne + "\n")
        f.write("----- FIN -----\n\n")


def sauvegarder_mail_envoye(expediteur: str, destinataires: list[str], lignes_message: list[str]) -> None:
    """
    Sauvegarde une copie du mail dans la boîte 'envoyés' de l'expéditeur.
    (Pas obligatoire pour V1, mais propre pour la suite.)
    """
    chemin_fichier = os.path.join(SENT_DIR, f"{expediteur}.txt")

    with open(chemin_fichier, "a", encoding="utf-8") as f:
        f.write(f"FROM: {expediteur}\n")
        f.write("TO: " + ", ".join(destinataires) + "\n")
        f.write("----- MESSAGE -----\n")
        for ligne in lignes_message:
            f.write(ligne + "\n")
        f.write("----- FIN -----\n\n")
