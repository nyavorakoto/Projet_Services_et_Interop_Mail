import threading
import json
import os
from Utils.file_manager import sauvegarder_mail, sauvegarder_mail_envoye


##########################################
# Chargement des utilisateurs (users.json)
##########################################
def charger_utilisateurs():
    chemin = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "users.json")
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)

USERS = charger_utilisateurs()


class SMTPSession(threading.Thread):

    def __init__(self, client_socket, client_addr):
        super().__init__(daemon=True)
        self.client = client_socket
        self.addr = client_addr

        # État d’authentification
        self.authenticated_user = None
        self.temp_login = None
        self.waiting_for_password = False

        # État SMTP
        self.destinataires = []
        self.data_mode = False
        self.buffer_message = []
        self.buffer_reception = ""

        print(f"[CONNEXION] Nouveau client : {client_addr}")

    def envoyer(self, message: str):
        #Envoie une réponse SMTP
        self.client.sendall((message + "\r\n").encode("utf-8"))

    def run(self):
        # 220 SMTP Server Ready 
        self.envoyer("220 Serveur SMTP Prêt (Authentification Requise)")

        try:
            while True:
                data = self.client.recv(1024)
                if not data:
                    break

                self.buffer_reception += data.decode("utf-8")

                while "\r\n" in self.buffer_reception:
                    ligne, self.buffer_reception = self.buffer_reception.split("\r\n", 1)
                    print(f"[REÇU] {repr(ligne)}")

                    ###########
                    # MODE DATA
                    ###########
                    if self.data_mode:
                        if ligne == ".":
                            print("[SMTP] Fin DATA -> Sauvegarde du message")
                            self.terminer_data()
                        else:
                            self.buffer_message.append(ligne)
                        continue

                    cmd = ligne.upper()

                    ############
                    # AUTH LOGIN
                    ############
                    if cmd.startswith("LOGIN "):
                        self.traiter_login(ligne)
                        continue

                    if cmd.startswith("PASS "):
                        self.traiter_pass(ligne)
                        continue

                    # Si pas connecté -> refuser SMTP
                    if self.authenticated_user is None:
                        # 530 Authentication required
                        self.envoyer("530 Authentification requise")
                        continue

                    ################
                    # SMTP COMMANDES
                    ################
                    if cmd.startswith("RCPT TO:"):
                        self.traiter_rcpt(ligne)

                    elif cmd == "DATA":
                        self.traiter_data()

                    elif cmd == "QUIT":
                        # 221 Bye
                        self.envoyer("221 Au revoir")
                        return

                    else:
                        # 500 Command not recognized
                        self.envoyer(" ")

        finally:
            print(f"[CONNEXION] Fermeture de la connexion : {self.addr}")
            self.client.close()

    ##################
    # AUTHENTIFICATION
    ##################
    def traiter_login(self, ligne):
        email = ligne[6:].strip()

        if email in USERS:
            self.temp_login = email
            self.waiting_for_password = True
            # 331 login OK, besoin mdp
            self.envoyer("331 Authentification ok, en attente du mot de passe")
        else:
            # 530 User not found
            self.envoyer("530 Utilisateur non trouvé")

    def traiter_pass(self, ligne):
        if not self.waiting_for_password:
            self.envoyer("503 Mauvaise séquence, LOGIN d'abord")
            return

        password = ligne[5:].strip()

        if USERS[self.temp_login]["password"] == password:
            self.authenticated_user = self.temp_login
            self.waiting_for_password = False
            # 235 Authentication successful
            self.envoyer("235 Authentification réussie")
            print(f"[AUTH] {self.authenticated_user} connecté.")
        else:
            # 535 Authentication failed
            self.envoyer("535 Authentification échouée")

    #######
    # SMTP
    #######
    def traiter_rcpt(self, ligne):
        dest = ligne[8:].replace("<", "").replace(">", "").strip()
        self.destinataires.append(dest)
        # 250 Destinataire OK
        self.envoyer("250 Destinataire OK")

    def traiter_data(self):
        if not self.destinataires:
            # 503 besoin d'abord de RCPT TO
            self.envoyer("503 RCPT TO manquant")
            return

        self.data_mode = True
        self.buffer_message = []
        # 354 Entrée mail, finir avec un point pour terminer la saisie
        self.envoyer("354 Début de l'entrée du mail; terminer avec un point")

    def terminer_data(self):
        self.data_mode = False

        print(f"[MAIL] mail de {self.authenticated_user} vers {self.destinataires}")

        # Sauvegarde
        for dest in self.destinataires:
            sauvegarder_mail(dest, self.authenticated_user, self.buffer_message)

        sauvegarder_mail_envoye(self.authenticated_user, self.destinataires, self.buffer_message)

        # 250 Message accepté
        self.envoyer("250 Message envoyé")