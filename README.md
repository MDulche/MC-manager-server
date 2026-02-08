# 🎮 Minecraft Server Manager

Dashboard web complet pour gérer des serveurs Minecraft vanilla avec système multi-monde et configuration persistante.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Fonctionnalités

### 🌍 Gestion Multi-Monde
- **Création/Suppression** : Créer et supprimer des mondes indépendants
- **Switch instantané** : Basculer entre mondes sans perte de données
- **Configuration persistante** : Chaque monde garde ses paramètres (whitelist, max joueurs, gamerules)
- **Backups individuels** : Historique de backups par monde

### ⚙️ Installation & Mise à Jour Serveur
- **Installation automatique** : Téléchargement dernière version Minecraft depuis API Mojang
- **Mise à jour sécurisée** : Backup automatique avant MAJ serveur
- **Validation URL** : Vérification intégrité fichiers avant téléchargement
- **Interface graphique** : Installation/MAJ depuis le dashboard

### 👥 Gestion Joueurs
- **Whitelist intelligente** : Ajout joueurs via API Mojang (UUID automatique)
- **Actions rapides** : Kick, ban, retrait whitelist
- **Consultation en temps réel** : Liste joueurs connectés

### 💾 Backups & Sécurité
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


## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/MDulche/MC-manager-server/issues)
- **Discussions** : [GitHub Discussions](https://github.com/MDulche/MC-manager-server/discussions)

---

**⭐ Si ce projet t'aide, n'hésite pas à mettre une étoile !**

```

***

### **2. LICENSE (fichier LICENSE)**

```

MIT License

Copyright (c) 2026 MDulche

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

***

### **3. .gitignore (déjà créé mais voici la version finale)**

```


# Python

venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
.env
*.log

# Minecraft Server

server/current/*.jar
server/current/eula.txt
server/current/server.properties
server/current/whitelist.json
server/current/ops.json
server/current/banned-*.json
server/current/usercache.json
server/current/world/
server/current/logs/
server/current/crash-reports/
server/current/libraries/
server/current/versions/

# Mondes (terrain trop lourd)

worlds/*/world/region/
worlds/*/world/DIM-1/
worlds/*/world/DIM1/
worlds/*/world/playerdata/
worlds/*/world/stats/
worlds/*/world/data/
worlds/*/world/advancements/

# Backups (fichiers lourds)

backups/*.tar.gz
backups/*.zip
backups/worlds/*.zip
backups/server_backup_*

# Logs

logs/
*.log

# Système

.DS_Store
.current_world
Thumbs.db
desktop.ini

```

***

### **4. requirements.txt (déjà créé)**
# 🎮 Minecraft Server Manager

Dashboard web complet pour gérer des serveurs Minecraft vanilla avec système multi-monde et configuration persistante.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Fonctionnalités

### 🌍 Gestion Multi-Monde
- **Création/Suppression** : Créer et supprimer des mondes indépendants
- **Switch instantané** : Basculer entre mondes sans perte de données
- **Configuration persistante** : Chaque monde garde ses paramètres (whitelist, max joueurs, gamerules)
- **Backups individuels** : Historique de backups par monde

### ⚙️ Installation & Mise à Jour Serveur
- **Installation automatique** : Téléchargement dernière version Minecraft depuis API Mojang
- **Mise à jour sécurisée** : Backup automatique avant MAJ serveur
- **Validation URL** : Vérification intégrité fichiers avant téléchargement
- **Interface graphique** : Installation/MAJ depuis le dashboard

### 👥 Gestion Joueurs
- **Whitelist intelligente** : Ajout joueurs via API Mojang (UUID automatique)
- **Actions rapides** : Kick, ban, retrait whitelist
- **Consultation en temps réel** : Liste joueurs connectés

### 💾 Backups & Sécurité
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


## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/MDulche/MC-manager-server/issues)
- **Discussions** : [GitHub Discussions](https://github.com/MDulche/MC-manager-server/discussions)

---

**⭐ Si ce projet t'aide, n'hésite pas à mettre une étoile !**

```

***

### **2. LICENSE (fichier LICENSE)**

```

MIT License

Copyright (c) 2026 MDulche

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

***

### **3. .gitignore (déjà créé mais voici la version finale)**

```


# Python

venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
.env
*.log

# Minecraft Server

server/current/*.jar
server/current/eula.txt
server/current/server.properties
server/current/whitelist.json
server/current/ops.json
server/current/banned-*.json
server/current/usercache.json
server/current/world/
server/current/logs/
server/current/crash-reports/
server/current/libraries/
server/current/versions/

# Mondes (terrain trop lourd)

worlds/*/world/region/
worlds/*/world/DIM-1/
worlds/*/world/DIM1/
worlds/*/world/playerdata/
worlds/*/world/stats/
worlds/*/world/data/
worlds/*/world/advancements/

# Backups (fichiers lourds)

backups/*.tar.gz
backups/*.zip
backups/worlds/*.zip
backups/server_backup_*

# Logs

logs/
*.log

# Système

.DS_Store
.current_world
Thumbs.db
desktop.ini

```

***

### **4. requirements.txt (déjà créé)**

```

fastapi==0.115.5
uvicorn[standard]==0.32.1
jinja2==3.1.4
python-multipart==0.0.12
requests==2.32.3
apscheduler==3.10.4

```

***

## 📤 **Commandes pour tout pousser**

```bash
cd ~/minecraft-manager

# Créer README.md
nano README.md
# (Colle le contenu ci-dessus, Ctrl+X, Y, Enter)

# Créer LICENSE
nano LICENSE
# (Colle le contenu ci-dessus, Ctrl+X, Y, Enter)

# Vérifier .gitignore
cat .gitignore

# Ajouter tous les fichiers
git add README.md LICENSE .gitignore manager/requirements.txt install.sh

# Commit
git commit -m "📝 Documentation complète + License MIT"

# Push
git push
```
```

fastapi==0.115.5
uvicorn[standard]==0.32.1
jinja2==3.1.4
python-multipart==0.0.12
requests==2.32.3
apscheduler==3.10.4

```

***

## 📤 **Commandes pour tout pousser**

```bash
cd ~/minecraft-manager

# Créer README.md
nano README.md
# (Colle le contenu ci-dessus, Ctrl+X, Y, Enter)

# Créer LICENSE
nano LICENSE
# (Colle le contenu ci-dessus, Ctrl+X, Y, Enter)

# Vérifier .gitignore
cat .gitignore

# Ajouter tous les fichiers
git add README.md LICENSE .gitignore manager/requirements.txt install.sh

# Commit
git commit -m "📝 Documentation complète + License MIT"

# Push
git push
```
