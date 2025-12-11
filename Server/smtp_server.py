import socket
from .smtp_session import SMTPSession

HOST = "127.0.0.1"
PORT = 2525

def lancer_serveur():
    # Création du socket serveur
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        # Permet de réutiliser rapidement l'adresse/port après fermeture
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(5)

        print(f"[SERVEUR] SMTP lancé sur {HOST}:{PORT}")

        while True:
            # Accepte une nouvelle connexion
            client_socket, client_addr = srv.accept()
            print(f"[SERVEUR] Nouvelle connexion : {client_addr}")
            # Crée une session dédiée (thread) pour gérer le client
            session = SMTPSession(client_socket, client_addr)
            session.start()