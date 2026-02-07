import subprocess
from pathlib import Path
from collections import deque
from datetime import datetime
import threading
import time
import select
import shutil


SERVER_DIR = Path.home() / "minecraft-manager" / "server" / "current"
JAR_NAME = "server.jar"

_process = None
_log_buffer = deque(maxlen=200)
_log_thread = None

def _reader_thread(proc: subprocess.Popen):
    global _log_buffer
    import sys
    
    for line in iter(proc.stdout.readline, ''):
        if not line:
            break
        clean_line = line.rstrip('\r\n')
        if clean_line:
            _log_buffer.append(clean_line)
            print("[LOG]", clean_line, flush=True)  # flush immédiat terminal
    
    # Reste après fermeture
    remaining = proc.stdout.read()
    if remaining:
        for line in remaining.split('\n'):
            clean = line.rstrip('\r')
            if clean:
                _log_buffer.append(clean)
                print("[LOG]", clean, flush=True)



def start_server():
    global _process, _log_thread, _log_buffer, _log

    if _process is not None and _process.poll() is None:
        return False

    _log_buffer.clear()

    cmd = [
        "java",
        "-Djava.awt.headless=true",  # headless mode
        "-Djava.util.logging.SimpleFormatter.format=%1$tY-%1$tm-%1$td %1$tH:%1$tM:%1$tS %4$s: %2$s: %5$s%n",  # format logs
        "-Xmx1024M",
        "-Xms1024M",
        "-jar",
        JAR_NAME,
        "nogui",
    ]

    _process = subprocess.Popen(
        cmd,
        cwd=SERVER_DIR,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=0,
        universal_newlines=True,
    )

    _log_thread = threading.Thread(target=_reader_thread, args=(_process,), daemon=True)
    _log_thread.start()

    return True

def stop_server():
    global _process
    if _process is None or _process.poll() is not None:
        return False

    try:
        _process.stdin.write("stop\n")
        _process.stdin.flush()
        _process.wait(timeout=60)
    except:
        pass
    finally:
        _process = None  # ← CRUCIAL : nettoyer la référence
    
    return True

def send_command(command: str):
    global _process
    if _process is None or _process.poll() is not None:
        return False
    _process.stdin.write(command.strip() + "\n")
    _process.stdin.flush()
    return True

def is_running():
    global _process
    return _process is not None and _process.poll() is None

def get_logs():
    return list(_log_buffer)

import shutil
import time
from datetime import datetime

def backup_world():
    """Crée un backup zip du monde actuel dans son dossier dédié"""
    if not is_running():
        return {"success": False, "error": "Serveur arrêté"}
    
    world_path = SERVER_DIR / "world"
    if not world_path.exists():
        return {"success": False, "error": "Monde introuvable"}
    
    # Dossier backup spécifique au monde
    current_world_name = get_current_world()
    backup_dir = Path.home() / "minecraft-manager" / "backups" / "worlds" / current_world_name
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%M")
    backup_name = f"backup_{timestamp}"
    backup_path = backup_dir / backup_name
    
    try:
        send_command("say §e[BACKUP] Sauvegarde en cours...")
        send_command("save-all")
        time.sleep(2)
        
        shutil.make_archive(str(backup_path), 'zip', world_path)
        
        send_command("say §a[BACKUP] Terminé!")
        return {"success": True, "file": f"{backup_name}.zip", "world": current_world_name}
    except Exception as e:
        return {"success": False, "error": str(e)}



def stop_server_graceful():
    """Arrêt progressif avec countdown 5min"""
    global _process
    if _process is None or _process.poll() is not None:
        return False
    
    # Annonces countdown
    send_command("say §c[SERVEUR] Arrêt dans 5 minutes!")
    time.sleep(60)  # 1min
    
    send_command("say §c[SERVEUR] Arrêt dans 4 minutes!")
    time.sleep(60)
    
    send_command("say §c[SERVEUR] Arrêt dans 3 minutes!")
    time.sleep(60)
    
    send_command("say §c[SERVEUR] Arrêt dans 2 minutes!")
    time.sleep(60)
    
    send_command("say §c[SERVEUR] Arrêt dans 1 minute!")
    time.sleep(30)
    
    send_command("say §c[SERVEUR] Arrêt dans 30 secondes!")
    time.sleep(20)
    
    send_command("say §c[SERVEUR] Arrêt dans 10 secondes!")
    time.sleep(5)

    send_command("say §c[SERVEUR] Arrêt dans 5 secondes!")
    time.sleep(1)
    
    send_command("say §c[SERVEUR] Arrêt dans 4 secondes!")
    time.sleep(1)

    send_command("say §c[SERVEUR] Arrêt dans 3 secondes!")
    time.sleep(1)

    send_command("say §c[SERVEUR] Arrêt dans 2 secondes!")
    time.sleep(1)

    send_command("say §c[SERVEUR] Arrêt dans 1 secondes!")
    time.sleep(1)

    send_command("say §c[SERVEUR] Arrêt imminent!")
    time.sleep(1)

    # Arrêt propre
    esult = stop_server()
    _process = None  # ← Nettoyer ici aussi
    return stop_server()

def list_worlds():
    """Liste les mondes disponibles"""
    try:
        worlds_dir = Path.home() / "minecraft-manager" / "worlds"
        worlds_dir.mkdir(parents=True, exist_ok=True)
        
        worlds = []
        for world_folder in worlds_dir.iterdir():
            if world_folder.is_dir():
                worlds.append({"name": world_folder.name})
        return worlds
    except Exception as e:
        print(f"[ERROR list_worlds] {e}")
        return []


def get_current_world():
    """Retourne le nom du monde actif"""
    try:
        marker = Path.home() / "minecraft-manager" / ".current_world"
        if marker.exists():
            return marker.read_text().strip()
        return "world"
    except Exception as e:
        print(f"[ERROR get_current_world] {e}")
        return "world"


def switch_world(world_name):
    """Change de monde (serveur doit être arrêté)"""
    if is_running():
        return {"success": False, "error": "Serveur en cours, arrêtez-le d'abord"}
    
    worlds_dir = Path.home() / "minecraft-manager" / "worlds"
    source_world = worlds_dir / world_name
    
    if not source_world.exists():
        return {"success": False, "error": f"Monde '{world_name}' introuvable"}
    
    current_world = SERVER_DIR / "world"
    old_name = get_current_world()
    
    # Sauvegarder config monde actuel AVANT switch
    if current_world.exists() and old_name and old_name != world_name:
        print(f"[SWITCH] Sauvegarde config de '{old_name}'")
        
        # Capturer config actuelle depuis server.properties
        props = get_server_properties()
        current_config = {
            "max_players": int(props.get("max-players", "20")),
            "whitelist_enabled": props.get("white-list", "false") == "true",
            "whitelist_players": get_whitelist()
        }
        
        print(f"[SWITCH] Config capturée: {current_config}")
        
        # IMPORTANT : Sauvegarder dans worlds/{old_name}/config.json AVANT archivage
        save_world_config(old_name, current_config)
        print(f"[SWITCH] Config sauvegardée dans worlds/{old_name}/config.json")
        
        # Lire config.json existant pour le préserver
        backup_location = worlds_dir / old_name
        existing_config_file = backup_location / "config.json"
        config_backup = None
        
        if existing_config_file.exists():
            import json
            config_backup = json.loads(existing_config_file.read_text())
            print(f"[SWITCH] Config existante trouvée: {config_backup}")
        
        # Archiver monde actuel (supprimer ancien dossier)
        if backup_location.exists():
            shutil.rmtree(backup_location)
            print(f"[SWITCH] Ancien dossier {old_name} supprimé")
        
        # Déplacer monde actuel vers worlds/{old_name}/
        shutil.move(str(current_world), str(backup_location))
        print(f"[SWITCH] Monde archivé dans worlds/{old_name}/")
        
        # Réécrire config.json avec la config capturée (écrase whitelist.json du monde)
        save_world_config(old_name, current_config)
        print(f"[SWITCH] config.json réécrit après archivage")
    
    # Copier nouveau monde dans server/current/world
    shutil.copytree(str(source_world), str(current_world))
    print(f"[SWITCH] Monde '{world_name}' copié vers server/current/world")
    
    # Marquer monde actif
    marker = Path.home() / "minecraft-manager" / ".current_world"
    marker.write_text(world_name)
    print(f"[SWITCH] Monde actif: {world_name}")
    
    # Appliquer config du nouveau monde
    print(f"[SWITCH] Application config de '{world_name}'")
    result = apply_world_config(world_name)
    print(f"[SWITCH] Config appliquée: {result}")
    
    return {"success": True, "world": world_name, "config_applied": result}



def create_new_world(world_name):
    """Crée un nouveau monde en archivant l'actuel"""
    if is_running():
        return {"success": False, "error": "Serveur en cours, arrêtez-le d'abord"}
    
    if not world_name or "/" in world_name or "\\" in world_name:
        return {"success": False, "error": "Nom invalide"}
    
    worlds_dir = Path.home() / "minecraft-manager" / "worlds"
    worlds_dir.mkdir(parents=True, exist_ok=True)
    
    # Vérifie si monde existe déjà
    if (worlds_dir / world_name).exists():
        return {"success": False, "error": f"Le monde '{world_name}' existe déjà"}
    
    current_world = SERVER_DIR / "world"
    
    # Sauvegarder config du monde actuel AVANT archivage
    if current_world.exists():
        old_name = get_current_world()
        
        # Capturer config actuelle
        current_config = {
            "max_players": int(get_server_properties().get("max-players", "20")),
            "whitelist_enabled": get_server_properties().get("white-list", "false") == "true",
            "whitelist_players": get_whitelist()
        }
        save_world_config(old_name, current_config)
        
        # Archiver monde
        archive_location = worlds_dir / old_name
        if archive_location.exists():
            shutil.rmtree(archive_location)
        shutil.move(str(current_world), str(archive_location))
    
    # Créer config PAR DÉFAUT pour nouveau monde
    new_config = {
        "max_players": 20,
        "whitelist_enabled": False,
        "whitelist_players": []
    }
    save_world_config(world_name, new_config)
    
    # Appliquer config nouveau monde AVANT démarrage
    update_server_properties({
        "max-players": "20",
        "white-list": "false"
    })
    
    import json
    whitelist_file = SERVER_DIR / "whitelist.json"
    whitelist_file.write_text("[]")
    
    # Marquer futur monde
    marker = Path.home() / "minecraft-manager" / ".current_world"
    marker.write_text(world_name)
    
    return {"success": True, "message": f"Monde '{world_name}' sera créé au prochain démarrage (config par défaut appliquée)"}



def delete_world(world_name):
    """Supprime un monde et tous ses backups"""
    if is_running() and get_current_world() == world_name:
        return {"success": False, "error": "Impossible de supprimer le monde actif"}
    
    worlds_dir = Path.home() / "minecraft-manager" / "worlds"
    world_path = worlds_dir / world_name
    
    if not world_path.exists():
        return {"success": False, "error": "Monde introuvable"}
    
    # Supprimer dossier monde
    shutil.rmtree(world_path)
    
    # Supprimer backups
    backup_dir = Path.home() / "minecraft-manager" / "backups" / "worlds" / world_name
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    return {"success": True, "message": f"Monde '{world_name}' supprimé"}


def list_world_backups(world_name):
    """Liste les backups d'un monde spécifique"""
    backup_dir = Path.home() / "minecraft-manager" / "backups" / "worlds" / world_name
    if not backup_dir.exists():
        return []
    
    backups = sorted(backup_dir.glob("*.zip"), reverse=True)
    return [{
        "name": b.stem,
        "file": b.name,
        "size": b.stat().st_size,
        "date": b.stat().st_mtime
    } for b in backups]


def restore_backup(world_name, backup_file):
    """Restaure un backup (serveur doit être arrêté)"""
    if is_running():
        return {"success": False, "error": "Arrêtez le serveur d'abord"}
    
    backup_path = Path.home() / "minecraft-manager" / "backups" / "worlds" / world_name / backup_file
    if not backup_path.exists():
        return {"success": False, "error": "Backup introuvable"}
    
    current_world = SERVER_DIR / "world"
    
    # Backup sécurité monde actuel
    if current_world.exists():
        safety_backup = current_world.parent / f"world_before_restore_{int(time.time())}"
        shutil.move(str(current_world), str(safety_backup))
    
    # Extraire backup
    shutil.unpack_archive(str(backup_path), str(current_world))
    
    # Marquer monde actif
    marker = Path.home() / "minecraft-manager" / ".current_world"
    marker.write_text(world_name)
    
    return {"success": True, "message": f"Backup '{backup_file}' restauré"}

def get_server_properties():
    """Lit server.properties"""
    props_file = SERVER_DIR / "server.properties"
    if not props_file.exists():
        return {}
    
    props = {}
    for line in props_file.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            key, val = line.split('=', 1)
            props[key.strip()] = val.strip()
    return props


def update_server_properties(updates):
    """Modifie server.properties (serveur doit être arrêté)"""
    if is_running():
        return {"success": False, "error": "Arrêtez le serveur d'abord"}
    
    props_file = SERVER_DIR / "server.properties"
    if not props_file.exists():
        return {"success": False, "error": "server.properties introuvable"}
    
    lines = props_file.read_text().splitlines()
    new_lines = []
    
    for line in lines:
        if '=' in line and not line.startswith('#'):
            key = line.split('=', 1)[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}")
                del updates[key]
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Ajouter nouvelles clés si manquantes
    for key, val in updates.items():
        new_lines.append(f"{key}={val}")
    
    props_file.write_text('\n'.join(new_lines))
    return {"success": True}


def get_whitelist():
    """Lit whitelist.json"""
    whitelist_file = SERVER_DIR / "whitelist.json"
    if not whitelist_file.exists():
        return []
    
    import json
    try:
        return json.loads(whitelist_file.read_text())
    except:
        return []


def add_to_whitelist(username):
    """Ajoute joueur à whitelist avec UUID Mojang"""
    import json
    import requests
    
    whitelist_file = SERVER_DIR / "whitelist.json"
    
    if not whitelist_file.exists():
        whitelist_file.write_text("[]")
    
    whitelist = get_whitelist()
    
    # Vérifier si déjà présent
    if any(p['name'].lower() == username.lower() for p in whitelist):
        return {"success": False, "error": "Joueur déjà dans whitelist"}
    
    # Récupérer UUID Mojang
    try:
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            real_username = data['name']
            uuid_raw = data['id']
            # Formater UUID avec tirets
            uuid_formatted = f"{uuid_raw[0:8]}-{uuid_raw[8:12]}-{uuid_raw[12:16]}-{uuid_raw[16:20]}-{uuid_raw[20:32]}"
        else:
            return {"success": False, "error": f"Joueur '{username}' introuvable (compte Mojang invalide)"}
    except Exception as e:
        return {"success": False, "error": f"Erreur API Mojang: {str(e)}"}
    
    # Ajouter avec vrai UUID
    whitelist.append({
        "uuid": uuid_formatted,
        "name": real_username
    })
    
    whitelist_file.write_text(json.dumps(whitelist, indent=2))
    
    # Activer whitelist
    props = get_server_properties()
    if props.get("white-list") != "true":
        if not is_running():
            update_server_properties({"white-list": "true"})
    
    if is_running():
        send_command("whitelist reload")

    # Sauvegarder dans config monde actuel
    current_world_name = get_current_world()
    world_config = get_world_config(current_world_name)
    world_config["whitelist_players"] = get_whitelist()
    save_world_config(current_world_name, world_config)

    return {"success": True, "added": real_username}




def remove_from_whitelist(username):
    """Retire joueur de whitelist"""
    import json
    
    whitelist_file = SERVER_DIR / "whitelist.json"
    whitelist = get_whitelist()
    
    whitelist = [p for p in whitelist if p['name'].lower() != username.lower()]
    whitelist_file.write_text(json.dumps(whitelist, indent=2))
    
    if is_running():
        send_command("whitelist reload")
        send_command(f"kick {username} Retiré de la whitelist")
    
    return {"success": True}


def kick_player(username):
    """Kick joueur"""
    if not is_running():
        return {"success": False, "error": "Serveur arrêté"}
    
    send_command(f"kick {username}")
    return {"success": True}


def ban_player(username):
    """Ban joueur"""
    if not is_running():
        return {"success": False, "error": "Serveur arrêté"}
    
    send_command(f"ban {username}")
    return {"success": True}


def apply_gamerule(rule_name, value):
    """Applique gamerule"""
    if not is_running():
        return {"success": False, "error": "Serveur arrêté"}
    
    send_command(f"gamerule {rule_name} {value}")
    return {"success": True}
def get_world_config(world_name):
    """Lit config spécifique d'un monde"""
    import json
    config_file = Path.home() / "minecraft-manager" / "worlds" / world_name / "config.json"
    
    if not config_file.exists():
        # Config par défaut
        return {
            "max_players": 20,
            "whitelist_enabled": False,
            "whitelist_players": []
        }
    
    try:
        return json.loads(config_file.read_text())
    except:
        return {"max_players": 20, "whitelist_enabled": False, "whitelist_players": []}


def save_world_config(world_name, config):
    """Sauvegarde config d'un monde"""
    import json
    worlds_dir = Path.home() / "minecraft-manager" / "worlds" / world_name
    worlds_dir.mkdir(parents=True, exist_ok=True)
    config_file = worlds_dir / "config.json"
    config_file.write_text(json.dumps(config, indent=2))


def apply_world_config(world_name):
    """Applique config d'un monde au serveur (serveur arrêté)"""
    if is_running():
        return {"success": False, "error": "Arrêtez le serveur d'abord"}
    
    config = get_world_config(world_name)
    
    # Appliquer server.properties
    update_server_properties({
        "max-players": str(config["max_players"]),
        "white-list": "true" if config["whitelist_enabled"] else "false"
    })
    
    # Appliquer whitelist.json
    import json
    whitelist_file = SERVER_DIR / "whitelist.json"
    whitelist_file.write_text(json.dumps(config["whitelist_players"], indent=2))
    
    return {"success": True}

def restart_server():
    """Redémarre le serveur proprement"""
    if not is_running():
        return {"success": False, "error": "Serveur déjà arrêté"}
    
    send_command("say §e[RESTART] Redémarrage en cours...")
    time.sleep(2)
    stop_server()
    time.sleep(3)
    start_server()
    
    return {"success": True}

# Système demandes whitelist
_whitelist_requests = []  # Cache mémoire des demandes

def check_for_whitelist_requests():
    """Parse logs pour détecter connexions refusées"""
    global _whitelist_requests, _log_buffer
    
    for line in list(_log_buffer)[-50:]:  # 50 dernières lignes
        if "You are not white-listed on this server!" in line and "Disconnecting" in line:
            try:
                parts = line.split("Disconnecting ")[1].split(" ")
                username = parts[0]
                
                # Chercher UUID dans logs précédents
                uuid = None
                for prev_line in list(_log_buffer)[-100:]:
                    if f"UUID of player {username} is" in prev_line:
                        uuid = prev_line.split("is ")[-1].strip()
                        break
                
                if uuid and username not in [r['name'] for r in _whitelist_requests]:
                    _whitelist_requests.append({
                        "name": username,
                        "uuid": uuid,
                        "timestamp": datetime.now().isoformat()
                    })
            except:
                pass
    
    return _whitelist_requests


def approve_whitelist_request(username):
    """Approuve demande et ajoute à whitelist"""
    global _whitelist_requests
    import json
    
    request = next((r for r in _whitelist_requests if r['name'] == username), None)
    if not request:
        return {"success": False, "error": "Demande introuvable"}
    
    whitelist_file = SERVER_DIR / "whitelist.json"
    if not whitelist_file.exists():
        whitelist_file.write_text("[]")
    
    whitelist = get_whitelist()
    
    whitelist.append({
        "uuid": request['uuid'],
        "name": request['name']
    })
    
    whitelist_file.write_text(json.dumps(whitelist, indent=2))
    
    _whitelist_requests = [r for r in _whitelist_requests if r['name'] != username]
    
    if is_running():
        send_command("whitelist reload")
    
    # Sauvegarder dans config monde
    current_world_name = get_current_world()
    world_config = get_world_config(current_world_name)
    world_config["whitelist_players"] = get_whitelist()
    save_world_config(current_world_name, world_config)
    
    return {"success": True, "message": f"{username} approuvé"}


def reject_whitelist_request(username):
    """Rejette demande"""
    global _whitelist_requests
    _whitelist_requests = [r for r in _whitelist_requests if r['name'] != username]
    return {"success": True}
# ============================================================
# INSTALLATION / MISE À JOUR SERVEUR MINECRAFT
# ============================================================

def get_latest_minecraft_version():
    """Récupère la dernière version stable de Minecraft depuis l'API officielle"""
    import requests
    try:
        # API Mojang officielle
        response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=10)
        data = response.json()
        
        # Dernière version stable (release)
        latest_release = data["latest"]["release"]
        
        # Trouver l'URL du server.jar
        for version in data["versions"]:
            if version["id"] == latest_release and version["type"] == "release":
                # Récupérer manifest de cette version
                version_response = requests.get(version["url"], timeout=10)
                version_data = version_response.json()
                
                # URL du server.jar
                server_url = version_data["downloads"]["server"]["url"]
                server_size = version_data["downloads"]["server"]["size"]
                
                return {
                    "version": latest_release,
                    "url": server_url,
                    "size_mb": round(server_size / 1024 / 1024, 2)
                }
        
        return None
    except Exception as e:
        print(f"[ERROR] Récupération version: {e}")
        return None


def check_server_installed():
    """Vérifie si un serveur Minecraft est déjà installé"""
    server_jar = SERVER_DIR / "server.jar"
    return server_jar.exists()


def get_current_server_version():
    """Récupère la version actuelle du serveur installé"""
    import subprocess
    import re
    
    server_jar = SERVER_DIR / "server.jar"
    if not server_jar.exists():
        return None
    
    try:
        # Exécuter java -jar server.jar --version
        result = subprocess.run(
            ["java", "-jar", str(server_jar), "--version"],
            cwd=str(SERVER_DIR),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parser sortie pour extraire version
        output = result.stdout + result.stderr
        match = re.search(r'(\d+\.\d+\.?\d*)', output)
        
        if match:
            return match.group(1)
        
        return "Version inconnue"
    except Exception as e:
        print(f"[ERROR] Détection version: {e}")
        return "Erreur détection"


def backup_server_before_update():
    """Sauvegarde complète du serveur AVANT mise à jour"""
    from datetime import datetime
    
    if is_running():
        return {"success": False, "error": "Arrêtez le serveur avant mise à jour"}
    
    # 1. Archiver monde actuel d'abord
    current_world_name = get_current_world()
    if current_world_name:
        current_world = SERVER_DIR / "world"
        if current_world.exists():
            print(f"[BACKUP] Archivage monde '{current_world_name}'")
            
            # Sauvegarder config
            props = get_server_properties()
            config = {
                "max_players": int(props.get("max-players", "20")),
                "whitelist_enabled": props.get("white-list", "false") == "true",
                "whitelist_players": get_whitelist()
            }
            save_world_config(current_world_name, config)
            
            # Archiver monde
            worlds_dir = Path.home() / "minecraft-manager" / "worlds"
            backup_location = worlds_dir / current_world_name
            if backup_location.exists():
                shutil.rmtree(backup_location)
            shutil.move(str(current_world), str(backup_location))
            
            # Réécrire config
            save_world_config(current_world_name, config)
            print(f"[BACKUP] Monde archivé dans worlds/{current_world_name}/")
    
    # 2. Créer backup complet serveur
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"server_backup_{timestamp}.tar.gz"
    backup_path = Path.home() / "minecraft-manager" / "backups" / backup_name
    
    try:
        # Compresser TOUT le dossier server/current
        import subprocess
        subprocess.run([
            "tar", "-czf", str(backup_path),
            "-C", str(SERVER_DIR.parent),
            "current"
        ], check=True)
        
        size_mb = round(backup_path.stat().st_size / 1024 / 1024, 2)
        
        print(f"[BACKUP] Serveur sauvegardé: {backup_name} ({size_mb} MB)")
        
        return {
            "success": True,
            "backup_file": backup_name,
            "size_mb": size_mb
        }
    except Exception as e:
        print(f"[ERROR] Backup serveur: {e}")
        return {"success": False, "error": str(e)}


def install_minecraft_server(download_url):
    """Installe un serveur Minecraft depuis une URL"""
    import requests
    
    if is_running():
        return {"success": False, "error": "Arrêtez le serveur avant installation"}
    
    # Créer dossier server si n'existe pas
    SERVER_DIR.mkdir(parents=True, exist_ok=True)
    
    server_jar = SERVER_DIR / "server.jar"
    
    try:
        print(f"[INSTALL] Téléchargement depuis: {download_url}")
        
        # Téléchargement avec progress
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(server_jar, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        if downloaded % (1024 * 1024) == 0:  # Log chaque MB
                            print(f"[INSTALL] Progression: {progress:.1f}%")
        
        print(f"[INSTALL] Téléchargement terminé: {round(downloaded / 1024 / 1024, 2)} MB")
        
        # Accepter EULA automatiquement
        eula_file = SERVER_DIR / "eula.txt"
        eula_file.write_text("eula=true\n")
        print("[INSTALL] EULA accepté")
        
        # Créer server.properties par défaut
        if not (SERVER_DIR / "server.properties").exists():
            default_props = """max-players=20
white-list=false
difficulty=normal
gamemode=survival
pvp=true
spawn-protection=16
motd=Minecraft Server Manager
server-port=25565
online-mode=true
"""
            (SERVER_DIR / "server.properties").write_text(default_props)
            print("[INSTALL] server.properties créé")
        
        # Créer whitelist.json vide
        if not (SERVER_DIR / "whitelist.json").exists():
            (SERVER_DIR / "whitelist.json").write_text("[]\n")
            print("[INSTALL] whitelist.json créé")
        
        return {"success": True, "message": "Serveur installé avec succès"}
        
    except Exception as e:
        print(f"[ERROR] Installation: {e}")
        # Nettoyer en cas d'erreur
        if server_jar.exists():
            server_jar.unlink()
        return {"success": False, "error": str(e)}


def update_minecraft_server(download_url):
    """Met à jour le serveur Minecraft (avec backup auto)"""
    
    # 1. Backup complet avant mise à jour
    print("[UPDATE] Création backup avant mise à jour...")
    backup_result = backup_server_before_update()
    
    if not backup_result["success"]:
        return backup_result
    
    # 2. Supprimer ancien server.jar
    server_jar = SERVER_DIR / "server.jar"
    if server_jar.exists():
        server_jar.unlink()
        print("[UPDATE] Ancien server.jar supprimé")
    
    # 3. Installer nouvelle version
    print("[UPDATE] Installation nouvelle version...")
    return install_minecraft_server(download_url)
