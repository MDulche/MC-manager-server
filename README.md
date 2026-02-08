# 🎮 Minecraft Server Manager

**Complete web dashboard to manage Minecraft vanilla servers with multi-world system and persistent configuration.**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

> *This project was developed with assistance from Perplexity AI (powered by Claude Sonnet 4.5)*

---

## 🌍 Languages / Langues

- [🇬🇧 English](#english-documentation)
- [🇫🇷 Français](#documentation-française)

---

# English Documentation

## ✨ Features

### 🌍 Multi-World Management
- **Create/Delete**: Create and delete independent worlds
- **Instant switch**: Switch between worlds without data loss
- **Persistent configuration**: Each world keeps its settings (whitelist, max players, gamerules)
- **Individual backups**: Backup history per world

### ⚙️ Server Installation & Updates
- **Automatic installation**: Download latest Minecraft version from Mojang API
- **Secure updates**: Automatic backup before server update
- **URL validation**: File integrity verification before download
- **Graphical interface**: Install/Update from dashboard

### 👥 Player Management
- **Smart whitelist**: Add players via Mojang API (automatic UUID)
- **Quick actions**: Kick, ban, remove from whitelist
- **Real-time monitoring**: Connected players list

### 💾 Backups & Security
- **Automatic backups**: Save every 30 minutes
- **Manual backups**: Instant backup button
- **Restoration**: Restore a world from its backups
- **Archiving**: Save before world switch/deletion

### 🎛️ Server Control
- **Live console**: Real-time logs with auto-refresh
- **Commands**: Send Minecraft commands from interface
- **Quick gamerules**: Preset buttons (Keep Inventory, Sleep 1 player, etc.)
- **Auto-restart**: Scheduled restart every 2.5 hours with warnings
- **Graceful shutdown**: Save + 5-minute warning

### 📊 Interface
- **Responsive dashboard**: Modern HTML/CSS/JS interface
- **Auto-refresh**: Status, logs, players updated automatically
- **Server configuration**: Modify max players, whitelist from interface

## 🚀 Quick Installation

### One-line installation

```bash
curl -sSL https://raw.githubusercontent.com/MDulche/MC-manager-server/main/install.sh | bash
```

The script will automatically:

1. ✅ Install Python 3.12+, Java 21, Git
2. ✅ Clone the repository
3. ✅ Create folder structure
4. ✅ Install Python dependencies
5. ✅ Configure automatic startup (crontab)
6. ✅ Launch manager after 2 minutes

### Dashboard access

```
http://<SERVER_IP>:8000
```


## 📋 Requirements

- **System**: Ubuntu 20.04+ / Debian 11+
- **Python**: 3.12 or higher
- **Java**: 21 (OpenJDK, installed automatically)
- **RAM**: Minimum 2 GB (4 GB recommended for Minecraft server)
- **Disk**: 5 GB free minimum


## 🛠️ Manual Installation

### 1. Clone repository

```bash
git clone https://github.com/MDulche/MC-manager-server.git ~/minecraft-manager
cd ~/minecraft-manager
```


### 2. Create folder structure

```bash
mkdir -p server/current worlds backups/worlds logs manager/web/static
```


### 3. Install Python dependencies

```bash
cd manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


### 4. Launch manager

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```


### 5. (Optional) Auto-start on boot

```bash
# Create startup script
cat > ~/minecraft-manager/start.sh << 'EOF'
#!/bin/bash
cd ~/minecraft-manager/manager
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 >> ~/minecraft-manager/logs/manager.log 2>&1
EOF

chmod +x ~/minecraft-manager/start.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "@reboot ~/minecraft-manager/start.sh") | crontab -
```


## 📖 Usage

### First startup

1. Access dashboard: `http://<IP>:8000`
2. Click **"📥 Install Minecraft Server"**
3. Confirm installation (latest version auto-detected)
4. Wait for download (~50 MB)
5. Server ready to start

### Create a world

1. **"World Management" section** → Enter world name
2. Click **"Create new"**
3. Current world is automatically archived
4. Server restarts with new world

### Switch world

1. Select a world in dropdown list
2. Click **"Load"**
3. Confirm (server must be stopped)
4. World config is restored automatically

### Enable whitelist

1. **"Server Configuration" section**
2. Check **"Enable whitelist"**
3. Click **"Save"** (automatic restart)
4. Add players in **"Whitelist" section**

### Add player to whitelist

1. Enter Minecraft username
2. Click **"Add"**
3. UUID is fetched automatically via Mojang API

### Update server

1. Click **"🔄 Update Server"**
2. Check current vs new version
3. Confirm (automatic backup before update)
4. Wait for download
5. Server restarts with new version

### Restore backup

1. **"World Management" section** → Select a world
2. Click **"Backups"**
3. Choose a backup from list
4. Click **"Restore"**
5. Current world is saved before restoration

## 🔧 Useful Commands

### Manager management

```bash
# View manager logs
tail -f ~/minecraft-manager/logs/manager.log

# Stop manager
pkill -f "uvicorn app:app"

# Restart manager
~/minecraft-manager/start.sh &

# Check if manager is running
ps aux | grep uvicorn
```


### Minecraft server management

```bash
# Minecraft server logs
tail -f ~/minecraft-manager/server/current/logs/latest.log

# Stop server (brutal)
pkill -f "java.*server.jar"

# Check if server is running
ps aux | grep "java.*server.jar"
```


### Backup management

```bash
# List world backups
ls -lh ~/minecraft-manager/backups/worlds/

# List server backups (during updates)
ls -lh ~/minecraft-manager/backups/server_backup_*
```


## 📂 Project Structure

```
minecraft-manager/
├── manager/                    # Python FastAPI application
│   ├── app.py                 # Main routes
│   ├── core/
│   │   └── process_manager.py # Minecraft process management
│   ├── web/
│   │   ├── templates/         # Jinja2 HTML templates
│   │   │   ├── dashboard.html
│   │   │   ├── install_server.html
│   │   │   └── update_server.html
│   │   └── static/            # CSS/JS/Images (empty by default)
│   ├── venv/                  # Python virtual environment
│   └── requirements.txt       # Python dependencies
│
├── server/
│   └── current/               # Active Minecraft server
│       ├── server.jar
│       ├── eula.txt
│       ├── server.properties
│       ├── whitelist.json
│       └── logs/
│
├── worlds/                    # Saved worlds
│   ├── world1/
│   │   ├── config.json        # Persistent world config
│   │   └── world/             # Terrain data
│   └── world2/
│
├── backups/
│   ├── worlds/                # World backups (.zip)
│   └── server_backup_*.tar.gz # Server backups (before updates)
│
├── logs/
│   └── manager.log            # Web manager logs
│
├── install.sh                 # Installation script
├── start.sh                   # Startup script
└── README.md                  # Documentation
```


## 🔄 Technical Architecture

### Backend

- **FastAPI**: Asynchronous Python web framework
- **Uvicorn**: High-performance ASGI server
- **APScheduler**: Scheduler for automatic backups/restarts
- **Subprocess**: Java Minecraft process management
- **Requests**: Mojang/Minecraft API calls


### Frontend

- **HTML/CSS/JS Vanilla**: Responsive interface without framework
- **Server-Sent Events (SSE)**: Real-time log streaming
- **AJAX Fetch API**: Asynchronous backend communication


### Storage

- **JSON**: World configuration (`config.json`)
- **ZIP**: World backup archives
- **TAR.GZ**: Server backup archives


## 🔒 Security

- ✅ **No root execution**: Script refuses to run as root
- ✅ **UUID validation**: Player verification via official Mojang API
- ✅ **Automatic backups**: Data loss protection
- ✅ **Action confirmation**: JavaScript popup for critical actions
- ⚠️ **Port 8000 exposed**: Use reverse proxy (Nginx) in production


## 🚧 Known Limitations

- **Single Minecraft server**: No multi-server (1 Java instance)
- **No mods/plugins**: Vanilla server only (Paper/Spigot not supported)
- **No authentication**: Dashboard accessible without login (add Nginx auth in prod)
- **Fixed port 25565**: No dynamic server port change


## 🛣️ Roadmap

- [ ] Paper/Spigot/Fabric support
- [ ] User authentication (dashboard login)
- [ ] Multi-server (multiple Java instances)
- [ ] Upload/Download worlds via interface
- [ ] Metrics/Stats (players, TPS, RAM)
- [ ] Discord webhook notifications
- [ ] Docker support


## 🤝 Contribution

Contributions are welcome!

1. Fork the project
2. Create a branch (`git checkout -b feature/improvement`)
3. Commit (`git commit -m 'Add feature X'`)
4. Push (`git push origin feature/improvement`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 👤 Author

**MDulche**

- GitHub: [@MDulche](https://github.com/MDulche)
- Repository: [MC-manager-server](https://github.com/MDulche/MC-manager-server)


## 🙏 Acknowledgments

- [Mojang/Microsoft](https://www.minecraft.net/) - Minecraft
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Uvicorn](https://www.uvicorn.org/) - ASGI server
- [Perplexity AI](https://www.perplexity.ai/) - Development assistance (Claude Sonnet 4.5)


## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/MDulche/MC-manager-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MDulche/MC-manager-server/discussions)

---

**⭐ If this project helps you, don't hesitate to star it!**

---

# Documentation Française

## ✨ Fonctionnalités

### 🌍 Gestion Multi-Monde

- **Création/Suppression** : Créer et supprimer des mondes indépendants
- **Switch instantané** : Basculer entre mondes sans perte de données
- **Configuration persistante** : Chaque monde garde ses paramètres (whitelist, max joueurs, gamerules)
- **Backups individuels** : Historique de backups par monde


### ⚙️ Installation \& Mise à Jour Serveur

- **Installation automatique** : Téléchargement dernière version Minecraft depuis API Mojang
- **Mise à jour sécurisée** : Backup automatique avant MAJ serveur
- **Validation URL** : Vérification intégrité fichiers avant téléchargement
- **Interface graphique** : Installation/MAJ depuis le dashboard


### 👥 Gestion Joueurs

- **Whitelist intelligente** : Ajout joueurs via API Mojang (UUID automatique)
- **Actions rapides** : Kick, ban, retrait whitelist
- **Consultation en temps réel** : Liste joueurs connectés


### 💾 Backups \& Sécurité

- **Backups automatiques** : Sauvegarde toutes les 30 minutes
- **Backups manuels** : Bouton backup instantané
- **Restauration** : Restaurer un monde depuis ses backups
- **Archivage** : Sauvegarde avant switch/suppression monde


### 🎛️ Contrôle Serveur

- **Console live** : Logs temps réel avec auto-refresh
- **Commandes** : Envoi commandes Minecraft depuis l'interface
- **Gamerules rapides** : Boutons presets (Keep Inventory, Sleep 1 joueur, etc.)
- **Auto-restart** : Redémarrage programmé toutes les 2h30 avec avertissements
- **Arrêt gracieux** : Sauvegarde + avertissement 5 minutes


### 📊 Interface

- **Dashboard responsive** : Interface moderne HTML/CSS/JS
- **Refresh automatique** : Statut, logs, joueurs mis à jour automatiquement
- **Configuration serveur** : Modification max joueurs, whitelist depuis l'interface


## 🚀 Installation Rapide

### Installation en une ligne

```bash
curl -sSL https://raw.githubusercontent.com/MDulche/MC-manager-server/main/install.sh | bash
```

Le script va automatiquement :

1. ✅ Installer Python 3.12+, Java 21, Git
2. ✅ Cloner le repository
3. ✅ Créer la structure de dossiers
4. ✅ Installer les dépendances Python
5. ✅ Configurer le démarrage automatique (crontab)
6. ✅ Lancer le manager après 2 minutes

### Accès au dashboard

```
http://<IP_DU_SERVEUR>:8000
```


## 📋 Prérequis

- **Système** : Ubuntu 20.04+ / Debian 11+
- **Python** : 3.12 ou supérieur
- **Java** : 21 (OpenJDK, installé automatiquement)
- **RAM** : Minimum 2 Go (4 Go recommandé pour serveur Minecraft)
- **Disque** : 5 Go libres minimum


## 🛠️ Installation Manuelle

### 1. Cloner le repository

```bash
git clone https://github.com/MDulche/MC-manager-server.git ~/minecraft-manager
cd ~/minecraft-manager
```


### 2. Créer structure de dossiers

```bash
mkdir -p server/current worlds backups/worlds logs manager/web/static
```


### 3. Installer dépendances Python

```bash
cd manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


### 4. Lancer le manager

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```


### 5. (Optionnel) Démarrage automatique au boot

```bash
# Créer script de démarrage
cat > ~/minecraft-manager/start.sh << 'EOF'
#!/bin/bash
cd ~/minecraft-manager/manager
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 >> ~/minecraft-manager/logs/manager.log 2>&1
EOF

chmod +x ~/minecraft-manager/start.sh

# Ajouter au crontab
(crontab -l 2>/dev/null; echo "@reboot ~/minecraft-manager/start.sh") | crontab -
```


## 📖 Utilisation

### Premier démarrage

1. Accéder au dashboard : `http://<IP>:8000`
2. Cliquer sur **"📥 Installer Serveur Minecraft"**
3. Confirmer l'installation (dernière version automatiquement détectée)
4. Attendre le téléchargement (~50 Mo)
5. Le serveur sera prêt à démarrer

### Créer un monde

1. **Section "Gestion mondes"** → Entrer nom du monde
2. Cliquer **"Créer nouveau"**
3. Le monde actuel est automatiquement archivé
4. Le serveur redémarre avec le nouveau monde

### Changer de monde

1. Sélectionner un monde dans la liste déroulante
2. Cliquer **"Charger"**
3. Confirmer (le serveur doit être arrêté)
4. La config du monde est restaurée automatiquement

### Activer la whitelist

1. **Section "Configuration serveur"**
2. Cocher **"Activer whitelist"**
3. Cliquer **"Sauvegarder"** (redémarrage automatique)
4. Ajouter joueurs dans **"Section Whitelist"**

### Ajouter un joueur à la whitelist

1. Entrer le pseudo Minecraft
2. Cliquer **"Ajouter"**
3. L'UUID est récupéré automatiquement via API Mojang

### Mettre à jour le serveur

1. Cliquer **"🔄 Mettre à Jour Serveur"**
2. Vérifier version actuelle vs nouvelle
3. Confirmer (backup automatique avant MAJ)
4. Attendre le téléchargement
5. Le serveur redémarre avec la nouvelle version

### Restaurer un backup

1. **Section "Gestion mondes"** → Sélectionner un monde
2. Cliquer **"Backups"**
3. Choisir un backup dans la liste
4. Cliquer **"Restaurer"**
5. Le monde actuel est sauvegardé avant restauration

## 🔧 Commandes Utiles

### Gestion du manager

```bash
# Voir les logs du manager
tail -f ~/minecraft-manager/logs/manager.log

# Arrêter le manager
pkill -f "uvicorn app:app"

# Redémarrer le manager
~/minecraft-manager/start.sh &

# Vérifier si le manager tourne
ps aux | grep uvicorn
```


### Gestion du serveur Minecraft

```bash
# Logs serveur Minecraft
tail -f ~/minecraft-manager/server/current/logs/latest.log

# Arrêter le serveur (brutal)
pkill -f "java.*server.jar"

# Vérifier si le serveur tourne
ps aux | grep "java.*server.jar"
```


### Gestion des backups

```bash
# Lister les backups de mondes
ls -lh ~/minecraft-manager/backups/worlds/

# Lister les backups serveur (lors des MAJ)
ls -lh ~/minecraft-manager/backups/server_backup_*
```


## 📂 Structure du Projet

```
minecraft-manager/
├── manager/                    # Application Python FastAPI
│   ├── app.py                 # Routes principales
│   ├── core/
│   │   └── process_manager.py # Gestion processus Minecraft
│   ├── web/
│   │   ├── templates/         # Templates HTML Jinja2
│   │   │   ├── dashboard.html
│   │   │   ├── install_server.html
│   │   │   └── update_server.html
│   │   └── static/            # CSS/JS/Images (vide par défaut)
│   ├── venv/                  # Environnement virtuel Python
│   └── requirements.txt       # Dépendances Python
│
├── server/
│   └── current/               # Serveur Minecraft actif
│       ├── server.jar
│       ├── eula.txt
│       ├── server.properties
│       ├── whitelist.json
│       └── logs/
│
├── worlds/                    # Mondes sauvegardés
│   ├── monde1/
│   │   ├── config.json        # Config persistante du monde
│   │   └── world/             # Données terrain
│   └── monde2/
│
├── backups/
│   ├── worlds/                # Backups des mondes (.zip)
│   └── server_backup_*.tar.gz # Backups serveur (avant MAJ)
│
├── logs/
│   └── manager.log            # Logs du manager web
│
├── install.sh                 # Script d'installation
├── start.sh                   # Script de démarrage
└── README.md                  # Documentation
```


## 🔄 Architecture Technique

### Backend

- **FastAPI** : Framework web Python asynchrone
- **Uvicorn** : Serveur ASGI haute performance
- **APScheduler** : Scheduler pour backups/restarts automatiques
- **Subprocess** : Gestion processus Java Minecraft
- **Requests** : Appels API Mojang/Minecraft


### Frontend

- **HTML/CSS/JS Vanilla** : Interface responsive sans framework
- **Server-Sent Events (SSE)** : Streaming logs temps réel
- **AJAX Fetch API** : Communication asynchrone avec backend


### Stockage

- **JSON** : Configuration mondes (`config.json`)
- **ZIP** : Archives backups mondes
- **TAR.GZ** : Archives backups serveur


## 🔒 Sécurité

- ✅ **Pas d'exécution root** : Le script refuse de tourner en root
- ✅ **Validation UUID** : Vérification joueurs via API Mojang officielle
- ✅ **Backups automatiques** : Protection perte de données
- ✅ **Confirmation actions** : Popup JavaScript pour actions critiques
- ⚠️ **Port 8000 exposé** : Utiliser un reverse proxy (Nginx) en production


## 🚧 Limitations Connues

- **Un seul serveur Minecraft** : Pas de multi-serveur (1 instance Java)
- **Pas de mods/plugins** : Serveur vanilla uniquement (Paper/Spigot non supporté)
- **Pas d'authentification** : Dashboard accessible sans login (ajouter Nginx auth en prod)
- **Port 25565 fixe** : Pas de changement dynamique du port serveur


## 🛣️ Roadmap

- [ ] Support Paper/Spigot/Fabric
- [ ] Authentification utilisateurs (login dashboard)
- [ ] Multi-serveurs (plusieurs instances Java)
- [ ] Upload/Download mondes via interface
- [ ] Metrics/Stats (joueurs, TPS, RAM)
- [ ] Discord webhook notifications
- [ ] Support Docker


## 🤝 Contribution

Les contributions sont bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajout fonctionnalité X'`)
4. Push (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📄 License

MIT License - voir [LICENSE](LICENSE) pour détails.

## 👤 Auteur

**MDulche**

- GitHub: [@MDulche](https://github.com/MDulche)
- Repository: [MC-manager-server](https://github.com/MDulche/MC-manager-server)


## 🙏 Remerciements

- [Mojang/Microsoft](https://www.minecraft.net/) - Minecraft
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Uvicorn](https://www.uvicorn.org/) - Serveur ASGI
- [Perplexity AI](https://www.perplexity.ai/) - Assistance au développement (Claude Sonnet 4.5)


## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/MDulche/MC-manager-server/issues)
- **Discussions** : [GitHub Discussions](https://github.com/MDulche/MC-manager-server/discussions)

---

**⭐ Si ce projet t'aide, n'hésite pas à mettre une étoile !**

```

***
