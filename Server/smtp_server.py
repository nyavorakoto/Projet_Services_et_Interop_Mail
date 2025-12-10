import socket
from .smtp_session import SMTPSession

HOST = "0.0.0.0"
PORT = 2525

def lancer_serveur():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(5)

        print(f"[SERVEUR] SMTP lancé sur {HOST}:{PORT}")

        while True:
            client_socket, client_addr = srv.accept()
            print(f"[SERVEUR] Nouvelle connexion : {client_addr}")
            session = SMTPSession(client_socket, client_addr)
            session.start()
