import threading
import json
import os
from Utils.file_manager import sauvegarder_mail, sauvegarder_mail_envoye


# ----------------------------------------------------------
# Chargement des utilisateurs (users.json)
# ----------------------------------------------------------
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
        """Envoie une réponse SMTP avec CRLF."""
        self.client.sendall((message + "\r\n").encode("utf-8"))

    def run(self):
        self.envoyer("220 SMTP Server Ready (Auth Required)")

        try:
            while True:
                data = self.client.recv(1024)
                if not data:
                    break

                self.buffer_reception += data.decode("utf-8")

                while "\r\n" in self.buffer_reception:
                    ligne, self.buffer_reception = self.buffer_reception.split("\r\n", 1)
                    print(f"[REÇU] {repr(ligne)}")

                    # ---------------------------
                    # MODE DATA
                    # ---------------------------
                    if self.data_mode:
                        if ligne == ".":
                            print("[SMTP] Fin DATA → sauvegarde")
                            self.terminer_data()
                        else:
                            self.buffer_message.append(ligne)
                        continue

                    cmd = ligne.upper()

                    # ---------------------------
                    # AUTH LOGIN
                    # ---------------------------
                    if cmd.startswith("LOGIN "):
                        self.traiter_login(ligne)
                        continue

                    if cmd.startswith("PASS "):
                        self.traiter_pass(ligne)
                        continue

                    # Si pas connecté → refuser SMTP
                    if self.authenticated_user is None:
                        self.envoyer("530 Authentication required")
                        continue

                    # ---------------------------
                    # SMTP COMMANDES
                    # ---------------------------
                    if cmd.startswith("RCPT TO:"):
                        self.traiter_rcpt(ligne)

                    elif cmd == "DATA":
                        self.traiter_data()

                    elif cmd == "QUIT":
                        self.envoyer("221 Bye")
                        return

                    else:
                        self.envoyer("500 Command not recognized")

        finally:
            print(f"[CONNEXION] Fermeture : {self.addr}")
            self.client.close()

    # ==========================================================
    # AUTH
    # ==========================================================
    def traiter_login(self, ligne):
        email = ligne[6:].strip()

        if email in USERS:
            self.temp_login = email
            self.waiting_for_password = True
            self.envoyer("331 Username OK, need password")
        else:
            self.envoyer("530 User not found")

    def traiter_pass(self, ligne):
        if not self.waiting_for_password:
            self.envoyer("503 Bad sequence, LOGIN first")
            return

        password = ligne[5:].strip()

        if USERS[self.temp_login]["password"] == password:
            self.authenticated_user = self.temp_login
            self.waiting_for_password = False
            self.envoyer("235 Authentication successful")
            print(f"[AUTH] {self.authenticated_user} connecté.")
        else:
            self.envoyer("535 Authentication failed")

    # ==========================================================
    # SMTP
    # ==========================================================
    def traiter_rcpt(self, ligne):
        dest = ligne[8:].replace("<", "").replace(">", "").strip()
        self.destinataires.append(dest)
        self.envoyer("250 Recipient OK")

    def traiter_data(self):
        if not self.destinataires:
            self.envoyer("503 Need RCPT TO first")
            return

        self.data_mode = True
        self.buffer_message = []
        self.envoyer("354 Start mail input; end with <CRLF>.<CRLF>")

    def terminer_data(self):
        self.data_mode = False

        print(f"[MAIL] {self.authenticated_user} → {self.destinataires}")

        # Sauvegarde
        for dest in self.destinataires:
            sauvegarder_mail(dest, self.authenticated_user, self.buffer_message)

        sauvegarder_mail_envoye(self.authenticated_user, self.destinataires, self.buffer_message)

        self.envoyer("250 Message accepted for delivery")
