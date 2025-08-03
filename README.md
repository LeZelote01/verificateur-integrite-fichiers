# 🛡️ Vérificateur d'Intégrité de Fichiers

## 📖 Description

Le **Vérificateur d'Intégrité de Fichiers** est un outil de sécurité informatique qui permet de surveiller l'intégrité des fichiers système en calculant et comparant leurs empreintes cryptographiques (MD5, SHA1, SHA256, SHA512). Il détecte automatiquement les modifications non autorisées et génère des alertes.

## ✨ Fonctionnalités

### 🔐 Calcul d'empreintes
- Support de **4 algorithmes** : MD5, SHA1, SHA256, SHA512
- Calcul optimisé pour les **gros fichiers** (lecture par blocs)
- Gestion des **erreurs de permission**

### 📊 Base de données d'empreintes
- Stockage au **format JSON**
- Métadonnées complètes : taille, date de modification, statut
- **Sauvegarde automatique** des modifications

### 🔍 Surveillance avancée
- Ajout de **fichiers individuels** ou **répertoires entiers**
- **Parcours récursif** des sous-dossiers
- **Filtrage par extensions** de fichiers
- **Vérification individuelle** ou **en lot**

### 📈 Rapports détaillés
- **Rapports texte** avec résumé et détails
- **Affichage temps réel** des vérifications
- **Historique** des modifications détectées

### 🚨 Détection de modifications
- **Alertes immédiates** lors de modifications
- **Suivi des fichiers manquants**
- **Conservation de l'historique** des empreintes

## 📋 Prérequis

- **Python 3.8+**
- Modules standard Python (aucune dépendance externe)

## 🚀 Installation

1. **Cloner ou télécharger** ce projet
```bash
cd 01-verificateur-integrite-fichiers
```

2. **Vérifier Python** (optionnel)
```bash
python --version  # Doit être >= 3.8
```

3. **Rendre le script exécutable** (Linux/Mac)
```bash
chmod +x file_integrity_checker.py
```

## 💡 Utilisation

### Interface en ligne de commande

```bash
python file_integrity_checker.py [command] [options]
```

### 📝 Commandes disponibles

#### 1. Ajouter un fichier à la surveillance
```bash
python file_integrity_checker.py add /path/to/file
python file_integrity_checker.py add /path/to/file --algorithm sha512
```

#### 2. Ajouter un répertoire complet
```bash
# Répertoire seul
python file_integrity_checker.py add-dir /path/to/directory

# Répertoire + sous-dossiers
python file_integrity_checker.py add-dir /path/to/directory --recursive

# Filtrer par extensions
python file_integrity_checker.py add-dir /path/to/directory -r --extensions .py .txt .conf
```

#### 3. Vérifier un fichier spécifique
```bash
python file_integrity_checker.py check /path/to/file
```

#### 4. Vérifier tous les fichiers surveillés
```bash
python file_integrity_checker.py check-all
```

#### 5. Lister tous les fichiers surveillés
```bash
python file_integrity_checker.py list
```

#### 6. Générer un rapport détaillé
```bash
python file_integrity_checker.py report
python file_integrity_checker.py report --output my_report.txt
```

#### 7. Retirer un fichier de la surveillance
```bash
python file_integrity_checker.py remove /path/to/file
```

### 🎛️ Options avancées

- `--algorithm`, `-a` : Algorithme de hashing (md5, sha1, sha256, sha512)
- `--database`, `-d` : Fichier de base de données personnalisé
- `--recursive`, `-r` : Parcours récursif pour les répertoires
- `--extensions`, `-e` : Extensions à inclure
- `--output`, `-o` : Fichier de sortie pour les rapports

### 📊 Exemples d'utilisation pratique

#### Surveiller les fichiers de configuration système
```bash
# Linux
python file_integrity_checker.py add-dir /etc --recursive --extensions .conf .cfg .ini

# Windows
python file_integrity_checker.py add-dir "C:\Windows\System32" --extensions .dll .exe
```

#### Vérification quotidienne automatisée
```bash
# Vérifier et générer un rapport
python file_integrity_checker.py check-all
python file_integrity_checker.py report --output "rapport_$(date +%Y%m%d).txt"
```

#### Surveillance de projet de développement
```bash
python file_integrity_checker.py add-dir ./src --recursive --extensions .py .js .html .css
python file_integrity_checker.py check-all
```

## 📁 Structure des fichiers

```
01-verificateur-integrite-fichiers/
├── file_integrity_checker.py      # Script principal
├── requirements.txt                # Dépendances (aucune)
├── README.md                      # Documentation
├── integrity_database.json       # Base de données (créée automatiquement)
└── integrity_report.txt          # Rapports générés
```

## 🔧 Configuration

### Base de données personnalisée
```bash
python file_integrity_checker.py add /path/to/file --database my_database.json
```

### Algorithmes recommandés par usage

- **SHA256** : Usage général (recommandé)
- **SHA512** : Sécurité maximale
- **MD5** : Compatibilité legacy (déconseillé pour la sécurité)
- **SHA1** : Compromis performance/sécurité

## 🎯 Cas d'usage

### 🔒 Sécurité informatique
- Détection d'intrusions
- Surveillance de fichiers critiques
- Audit de conformité
- Vérification post-incident

### 🏢 Administration système
- Monitoring des configurations
- Vérification d'intégrité des sauvegardes
- Suivi des mises à jour
- Contrôle de versions de fichiers

### 💻 Développement
- Vérification de l'intégrité du code source
- Détection de modifications non autorisées
- Contrôle qualité des déploiements

## 🚨 Interprétation des résultats

### États des fichiers

- **✅ Intact** : Fichier non modifié depuis l'ajout
- **🚨 Modifié** : Empreinte différente détectée
- **❌ Manquant** : Fichier supprimé ou déplacé
- **⚠️ Erreur** : Problème d'accès au fichier

### Codes de sortie

- `0` : Succès
- `1` : Erreur ou interruption utilisateur

## 🔍 Résolution de problèmes

### Erreurs courantes

**"Permission denied"**
```bash
# Exécuter avec privilèges administrateur
sudo python file_integrity_checker.py add /path/to/protected/file
```

**"File not found"**
- Vérifier que le chemin est correct
- Utiliser des chemins absolus pour éviter les ambiguïtés

**Base de données corrompue**
```bash
# Supprimer et recréer la base
rm integrity_database.json
python file_integrity_checker.py add-dir /path/to/directory
```

## 📈 Performances

### Optimisations implémentées
- **Lecture par blocs** (8192 bytes) pour les gros fichiers
- **Gestion mémoire** optimisée
- **Sauvegarde différée** de la base de données

### Recommandations
- Utiliser SHA256 pour un bon équilibre performance/sécurité
- Éviter MD5 sur des fichiers critiques
- Programmer les vérifications durant les heures creuses

## 🔮 Améliorations futures

### Fonctionnalités prévues
- **Surveillance en temps réel** avec watchdog
- **Interface graphique** avec Tkinter
- **Notifications par email** lors de modifications
- **Intégration avec des logs systèmes**
- **Support des liens symboliques**
- **Compression de la base de données**

### Intégrations possibles
- **Cron** pour automatisation
- **Syslog** pour logging centralisé
- **SIEM** pour alertes sécurité
- **API REST** pour intégration applicative

## 📚 Références

- [Documentation Python hashlib](https://docs.python.org/3/library/hashlib.html)
- [NIST - Secure Hash Standards](https://csrc.nist.gov/publications/fips)
- [Guide de sécurité ANSSI](https://www.ssi.gouv.fr/)

## 👥 Contribution

Ce projet est open source. Les contributions sont les bienvenues :

1. **Fork** le projet
2. Créer une **branche** pour votre fonctionnalité
3. **Commiter** vos modifications
4. Ouvrir une **Pull Request**

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**Auteur** : Assistant IA  
**Version** : 1.0  
**Date** : Juillet 2025  
**Niveau** : Débutant  
**Temps de développement** : 1 semaine