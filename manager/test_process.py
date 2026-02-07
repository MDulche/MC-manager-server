from core.process_manager import start_server, stop_server, send_command, is_running
import time

print("Démarrage du serveur...")
start_server()
time.sleep(20)

print("Serveur en cours d'exécution :", is_running())
print("Envoi d'une commande /list...")
send_command("list")
time.sleep(5)

print("Arrêt du serveur...")
stop_server()
print("Serveur en cours d'exécution :", is_running())
