#!/bin/bash
set -e

echo "=========================================="
echo "  Installation Minecraft Manager"
echo "=========================================="
echo ""

# Vérification root
if [ "$EUID" -eq 0 ]; then 
    echo "❌ Ne pas exécuter en root/sudo"
    exit 1
fi

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Variables
INSTALL_DIR="$HOME/minecraft-manager"
GITHUB_USER="MDulche"
GITHUB_REPO="MC-manager-server"
GITHUB_BRANCH="main"

echo -e "${BLUE}[1/8]${NC} Vérification système..."

# Vérifier Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo -e "${RED}❌ Système non supporté (apt requis)${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Système compatible"

# Mise à jour packages
echo ""
echo -e "${BLUE}[2/8]${NC} Mise à jour système..."
sudo apt update -qq

# Installation dépendances système
echo ""
echo -e "${BLUE}[3/8]${NC} Installation dépendances système..."
echo "  - Python 3.12+"
echo "  - pip, venv, git"
echo "  - Java 21 (OpenJDK)"

sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    openjdk-21-jre-headless \
    curl \
    wget >/dev/null 2>&1

echo -e "${GREEN}✓${NC} Dépendances installées"

# Vérification versions
echo ""
echo -e "${BLUE}[4/8]${NC} Vérification versions..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
echo -e "  Python: ${GREEN}$PYTHON_VERSION${NC}"
echo -e "  Java:   ${GREEN}$JAVA_VERSION${NC}"

# Clonage repository
echo ""
echo -e "${BLUE}[5/8]${NC} Téléchargement projet depuis GitHub..."

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${RED}⚠️  Dossier $INSTALL_DIR existe déjà${NC}"
    read -p "Supprimer et réinstaller? (o/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        echo -e "${RED}❌ Installation annulée${NC}"
        exit 1
    fi
fi

git clone -b $GITHUB_BRANCH \
    "https://github.com/$GITHUB_USER/$GITHUB_REPO.git" \
    "$INSTALL_DIR" -q

echo -e "${GREEN}✓${NC} Projet téléchargé"

# Création structure dossiers
echo ""
echo -e "${BLUE}[6/8]${NC} Création structure dossiers..."
cd "$INSTALL_DIR"

mkdir -p server/current
mkdir -p worlds
mkdir -p backups/worlds
mkdir -p logs
mkdir -p manager/web/static

echo -e "${GREEN}✓${NC} Structure créée"

# Installation Python venv + dépendances
echo ""
echo -e "${BLUE}[7/8]${NC} Installation dépendances Python..."
cd "$INSTALL_DIR/manager"

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip -q
pip install -r requirements.txt -q

echo -e "${GREEN}✓${NC} Environnement Python configuré"

# Configuration Crontab
echo ""
echo -e "${BLUE}[8/8]${NC} Configuration démarrage automatique..."

# Créer script de démarrage
cat > "$INSTALL_DIR/start.sh" << 'EOFSTART'
#!/bin/bash
cd ~/minecraft-manager/manager
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 >> ~/minecraft-manager/logs/manager.log 2>&1
EOFSTART

chmod +x "$INSTALL_DIR/start.sh"

# Ajouter au crontab (démarrage au boot)
CRON_ENTRY="@reboot $INSTALL_DIR/start.sh"

# Supprimer anciennes entrées minecraft-manager
crontab -l 2>/dev/null | grep -v "minecraft-manager" | crontab - 2>/dev/null || true

# Ajouter nouvelle entrée
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo -e "${GREEN}✓${NC} Crontab configuré (démarrage automatique au boot)"

# Résumé installation
echo ""
echo -e "${GREEN}=========================================="
echo "  ✓ Installation terminée"
echo "==========================================${NC}"
echo ""
echo -e "📁 Emplacement: ${BLUE}$INSTALL_DIR${NC}"
echo ""
echo -e "${YELLOW}🚀 Le manager va démarrer dans 2 minutes...${NC}"
echo ""
echo -e "Pendant ce temps, voici ce qui a été configuré:"
echo ""
echo "1. Démarrage automatique au boot (crontab)"
echo "2. Logs disponibles: ~/minecraft-manager/logs/manager.log"
echo "3. Dashboard: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo -e "${BLUE}Commandes utiles:${NC}"
echo "  - Voir logs:     tail -f ~/minecraft-manager/logs/manager.log"
echo "  - Arrêter:       pkill -f 'uvicorn app:app'"
echo "  - Redémarrer:    ~/minecraft-manager/start.sh &"
echo ""
echo -e "📖 Documentation: https://github.com/$GITHUB_USER/$GITHUB_REPO"
echo ""

# Démarrage différé (2 minutes)
echo -e "${YELLOW}⏳ Démarrage dans 2 minutes (120s)...${NC}"
sleep 120

echo -e "${GREEN}🚀 Lancement du Minecraft Manager...${NC}"
cd "$INSTALL_DIR/manager"
source venv/bin/activate
nohup uvicorn app:app --host 0.0.0.0 --port 8000 >> "$INSTALL_DIR/logs/manager.log" 2>&1 &

sleep 3

echo ""
echo -e "${GREEN}✓ Manager démarré en arrière-plan${NC}"
echo ""
echo -e "Accéder au dashboard: ${BLUE}http://$(hostname -I | awk '{print $1}'):8000${NC}"
echo ""
