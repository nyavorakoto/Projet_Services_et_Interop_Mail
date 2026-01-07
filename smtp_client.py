import socket

HOST = "127.0.0.1"
PORT = 2525


def envoyer(sock, ligne):
    #Envoie une commande au serveur SMTP et affiche la réponse
    sock.sendall((ligne + "\r\n").encode("utf-8"))
    rep = sock.recv(1024).decode("utf-8").strip()
    return rep


def connexion_utilisateur(sock):
    #Boucle la connexion LOGIN + PASS jusqu'à réussite
    while True:
        print("\n===== Connexion utilisateur =====")
        email = input("Email : ").strip()
        password = input("Mot de passe : ").strip()

        rep = envoyer(sock, f"LOGIN {email}")
        if not rep.startswith("331"):
            print("Utilisateur inconnu. Réessayez.")
            continue

        rep = envoyer(sock, f"PASS {password}")
        if rep.startswith("235"):
            print(" Connexion réussie !\n")
            return email  # On renvoie l'utilisateur authentifié
        else:
            print("Mot de passe incorrect. Réessayez.")


def envoyer_un_mail(sock, expediteur):
    #Envoie un seul mail en réutilisant la connexion existante
    destinataire = input("Veuillez taper l'adresse mail du destinataire : ").strip()

    print("\n Veuillez saisir votre message ('.' pour terminer) :")
    lignes = []
    while True:
        ligne = input("> ")
        if ligne == ".":
            break
        lignes.append(ligne)

    # MAIL FROM (utilise l'expéditeur déjà authentifié)
    envoyer(sock, f"MAIL FROM:<{expediteur}>")

    # RCPT TO
    envoyer(sock, f"RCPT TO:<{destinataire}>")

    # DATA
    rep = envoyer(sock, "DATA")
    if not rep.startswith("354"):
        print("Erreur DATA.")
        return

    # Corps du message
    for l in lignes:
        sock.sendall((l + "\r\n").encode("utf-8"))

    # Fin
    sock.sendall(b".\r\n")
    print("<<<", sock.recv(1024).decode("utf-8").strip())

    print("\n Message envoyé avec succès !\n")


def main():
    # Connexion unique au serveur
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Message 220 du serveur
        rep = s.recv(1024).decode("utf-8").strip()
        print(rep)

        # PHASE D'IDENTIFICATION AUTOMATIQUE (logiciel SMTP)
        print("=== PHASE D'IDENTIFICATION SMTP ===")
        
        # Test EHLO automatique (sera rejeté - extensions non supportées)
        print("Test automatique EHLO...")
        envoyer(s, "EHLO smtp-client.local")
        
        # HELO automatique obligatoire (sera accepté)
        print("HELO automatique...")
        envoyer(s, "HELO smtp-client.local")
        
        #print(" Phase d'identification terminée\n")
        
        # Authentification (après identification seulement)
        expediteur_auth = connexion_utilisateur(s)

        # Boucle pour envoyer plusieurs mails sans se reconnecter
        while True:
            envoyer_un_mail(s, expediteur_auth)
            again = input("Envoyer un autre mail ? (o/n) : ").lower()
            if again != "o":
                break

        # Déconnexion finale
        envoyer(s, "QUIT")


if __name__ == "__main__":
    main()