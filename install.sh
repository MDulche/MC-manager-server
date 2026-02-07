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
NC='\033[0m'

# Variables
INSTALL_DIR="$HOME/minecraft-manager"
GITHUB_USER="MDulche"
GITHUB_REPO="MC-manager-server"
GITHUB_BRANCH="main"

echo -e "${BLUE}[1/6]${NC} Vérification système..."

# Vérifier Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo -e "${RED}❌ Système non supporté (apt requis)${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Système compatible"

# Mise à jour packages
echo ""
echo -e "${BLUE}[2/6]${NC} Mise à jour système..."
sudo apt update -qq

# Installation dépendances système
echo ""
echo -e "${BLUE}[3/6]${NC} Installation dépendances système..."
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
echo -e "${BLUE}[4/6]${NC} Vérification versions..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
echo -e "  Python: ${GREEN}$PYTHON_VERSION${NC}"
echo -e "  Java:   ${GREEN}$JAVA_VERSION${NC}"

# Clonage repository (UNIQUEMENT manager/)
echo ""
echo -e "${BLUE}[5/6]${NC} Téléchargement projet depuis GitHub..."

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

# Cloner le repo (contient manager/ + install.sh + README.md)
git clone -b $GITHUB_BRANCH \
    "https://github.com/$GITHUB_USER/$GITHUB_REPO.git" \
    "$INSTALL_DIR"

echo -e "${GREEN}✓${NC} Projet téléchargé"

# Création structure dossiers (IMPORTÉ : créer les dossiers ignorés par Git)
echo ""
echo -e "${BLUE}[6/6]${NC} Création structure dossiers..."
cd "$INSTALL_DIR"

# Créer les dossiers qui ne sont PAS sur GitHub
mkdir -p server/current
mkdir -p worlds
mkdir -p backups
mkdir -p logs

echo -e "${GREEN}✓${NC} Structure créée"

# Installation Python venv + dépendances
echo ""
echo -e "${BLUE}[7/7]${NC} Installation dépendances Python..."
cd "$INSTALL_DIR/manager"

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip -q
pip install -r requirements.txt -q

echo -e "${GREEN}✓${NC} Environnement Python configuré"

# Résumé installation
echo ""
echo -e "${GREEN}=========================================="
echo "  ✓ Installation terminée"
echo "==========================================${NC}"
echo ""
echo -e "📁 Emplacement: ${BLUE}$INSTALL_DIR${NC}"
echo ""
echo -e "🚀 Prochaines étapes:"
echo ""
echo "1. Lancer le manager:"
echo -e "   ${BLUE}cd $INSTALL_DIR/manager${NC}"
echo -e "   ${BLUE}source venv/bin/activate${NC}"
echo -e "   ${BLUE}uvicorn app:app --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "2. Accéder au dashboard:"
echo -e "   ${BLUE}http://$(hostname -I | awk '{print $1}'):8000${NC}"
echo ""
echo "3. Cliquer sur 'Installer Serveur Minecraft' dans le dashboard"
echo ""
echo -e "📖 Documentation: https://github.com/$GITHUB_USER/$GITHUB_REPO"
echo ""
