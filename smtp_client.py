import socket

HOST = "127.0.0.1"
PORT = 2525


def envoyer(sock, ligne):
    """Envoie une commande au serveur SMTP et affiche la réponse."""
    sock.sendall((ligne + "\r\n").encode("utf-8"))
    rep = sock.recv(1024).decode("utf-8").strip()
    print(f"<<< {rep}")
    return rep


def connexion_utilisateur(sock):
    """Boucle de connexion LOGIN + PASS jusqu'à réussite."""
    while True:
        print("\n===== Connexion utilisateur =====")
        email = input("Email : ").strip()
        password = input("Mot de passe : ").strip()

        rep = envoyer(sock, f"LOGIN {email}")
        if not rep.startswith("331"):
            print("❌ Utilisateur inconnu. Réessayez.")
            continue

        rep = envoyer(sock, f"PASS {password}")
        if rep.startswith("235"):
            print("✔ Connexion réussie !\n")
            return email  # On renvoie l'utilisateur authentifié
        else:
            print("❌ Mot de passe incorrect. Réessayez.")


def envoyer_message():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Message 220 du serveur
        rep = s.recv(1024).decode("utf-8").strip()
        print("<<<", rep)

        # Connexion obligatoire AVANT d'envoyer un mail
        expediteur = connexion_utilisateur(s)

        destinataire = input("Destinataire : ").strip()

        print("\nÉcris ton message ('.' pour terminer) :")
        lignes = []
        while True:
            ligne = input("> ")
            if ligne == ".":
                break
            lignes.append(ligne)

        # RCPT TO
        envoyer(s, f"RCPT TO:<{destinataire}>")

        # DATA
        rep = envoyer(s, "DATA")
        if not rep.startswith("354"):
            print("❌ Erreur DATA.")
            return

        # Corps du message
        for l in lignes:
            s.sendall((l + "\r\n").encode("utf-8"))

        # Fin
        s.sendall(b".\r\n")
        print("<<<", s.recv(1024).decode("utf-8").strip())

        envoyer(s, "QUIT")

        print("\n✔ Message envoyé avec succès !\n")


def main():
    while True:
        envoyer_message()
        again = input("Envoyer un autre mail ? (o/n) : ").lower()
        if again != "o":
            break


if __name__ == "__main__":
    main()
