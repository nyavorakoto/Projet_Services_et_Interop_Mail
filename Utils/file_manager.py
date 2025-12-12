import threading
import os

# Verrou pour éviter les accès simultanés
lock = threading.Lock()

def sauvegarder_mail(destinataire, expediteur, message_lines):
    #Sauvegarde un email dans la boîte de réception du destinataire
    with lock:  # Verrou pour thread-safety
        inbox_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "inbox")
        os.makedirs(inbox_dir, exist_ok=True)
        
        inbox_file = os.path.join(inbox_dir, f"{destinataire}.txt")
        
        # Ajouter le mail au fichier
        with open(inbox_file, "a", encoding="utf-8") as f:
            f.write(f"FROM: {expediteur}\n")
            f.write(f"TO: {destinataire}\n")
            f.write("----- MESSAGE -----\n")
            for ligne in message_lines:
                f.write(ligne + "\n")
            f.write("----- FIN -----\n\n")

def sauvegarder_mail_envoye(expediteur, destinataires, message_lines):
    #Sauvegarde un email dans les emails envoyés de l'expéditeur
    with lock:  # Verrou pour thread-safety
        sent_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "Sent")
        os.makedirs(sent_dir, exist_ok=True)
        
        sent_file = os.path.join(sent_dir, f"{expediteur}.txt")
        
        # Ajoute le mail au fichier
        with open(sent_file, "a", encoding="utf-8") as f:
            f.write(f"FROM: {expediteur}\n")
            f.write("TO: " + ", ".join(destinataires) + "\n")
            f.write("----- MESSAGE -----\n")
            for ligne in message_lines:
                f.write(ligne + "\n")
            f.write("----- FIN -----\n\n")