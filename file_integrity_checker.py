#!/usr/bin/env python3
"""
Vérificateur d'Intégrité de Fichiers
===================================

Outil pour surveiller l'intégrité des fichiers système en calculant et comparant
les empreintes MD5/SHA256. Détecte automatiquement les modifications non autorisées.

Auteur: Jean Yves (LeZelote)
Date: Mai 2025
Version: 1.0
"""

import os
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime
import argparse
import sys

class FileIntegrityChecker:
    """Classe principale pour vérifier l'intégrité des fichiers."""
    
    def __init__(self, db_path="integrity_database.json"):
        """
        Initialise le vérificateur d'intégrité.
        
        Args:
            db_path (str): Chemin vers la base de données des empreintes
        """
        self.db_path = db_path
        self.database = self._load_database()
        self.supported_algorithms = ['md5', 'sha1', 'sha256', 'sha512']
    
    def _load_database(self):
        """Charge la base de données des empreintes depuis le fichier JSON."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Erreur lors du chargement de la base: {e}")
                return {}
        return {}
    
    def _save_database(self):
        """Sauvegarde la base de données des empreintes dans le fichier JSON."""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.database, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return False
    
    def calculate_hash(self, file_path, algorithm='sha256'):
        """
        Calcule l'empreinte d'un fichier avec l'algorithme spécifié.
        
        Args:
            file_path (str): Chemin vers le fichier
            algorithm (str): Algorithme de hashing ('md5', 'sha1', 'sha256', 'sha512')
        
        Returns:
            str: Empreinte hexadécimale du fichier ou None en cas d'erreur
        """
        if algorithm not in self.supported_algorithms:
            raise ValueError(f"Algorithme non supporté: {algorithm}")
        
        hash_func = getattr(hashlib, algorithm)()
        
        try:
            with open(file_path, 'rb') as f:
                # Lecture par blocs pour gérer les gros fichiers
                while chunk := f.read(8192):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except (IOError, PermissionError) as e:
            print(f"❌ Erreur lecture fichier {file_path}: {e}")
            return None
    
    def add_file(self, file_path, algorithm='sha256'):
        """
        Ajoute un fichier à la base de données de surveillance.
        
        Args:
            file_path (str): Chemin vers le fichier
            algorithm (str): Algorithme de hashing à utiliser
        
        Returns:
            bool: True si ajouté avec succès, False sinon
        """
        if not os.path.isfile(file_path):
            print(f"❌ Le fichier n'existe pas: {file_path}")
            return False
        
        file_hash = self.calculate_hash(file_path, algorithm)
        if not file_hash:
            return False
        
        file_stats = os.stat(file_path)
        file_info = {
            'path': os.path.abspath(file_path),
            'hash': file_hash,
            'algorithm': algorithm,
            'size': file_stats.st_size,
            'modified_time': file_stats.st_mtime,
            'added_date': datetime.now().isoformat(),
            'last_check': datetime.now().isoformat(),
            'status': 'intact'
        }
        
        self.database[file_path] = file_info
        
        if self._save_database():
            print(f"✅ Fichier ajouté à la surveillance: {file_path}")
            print(f"   Hash {algorithm.upper()}: {file_hash}")
            return True
        return False
    
    def check_file(self, file_path):
        """
        Vérifie l'intégrité d'un fichier surveillé.
        
        Args:
            file_path (str): Chemin vers le fichier
        
        Returns:
            dict: Résultat de la vérification
        """
        if file_path not in self.database:
            return {
                'status': 'unknown',
                'message': 'Fichier non surveillé'
            }
        
        file_info = self.database[file_path]
        
        # Vérifier si le fichier existe toujours
        if not os.path.exists(file_path):
            file_info['status'] = 'missing'
            file_info['last_check'] = datetime.now().isoformat()
            return {
                'status': 'missing',
                'message': 'Fichier manquant',
                'details': file_info
            }
        
        # Calculer la nouvelle empreinte
        current_hash = self.calculate_hash(file_path, file_info['algorithm'])
        if not current_hash:
            return {
                'status': 'error',
                'message': 'Erreur lors du calcul de l\'empreinte'
            }
        
        # Comparer les empreintes
        if current_hash == file_info['hash']:
            file_info['status'] = 'intact'
            file_info['last_check'] = datetime.now().isoformat()
            result = {
                'status': 'intact',
                'message': 'Fichier intact',
                'details': file_info
            }
        else:
            file_info['status'] = 'modified'
            file_info['last_check'] = datetime.now().isoformat()
            file_info['previous_hash'] = file_info['hash']
            file_info['current_hash'] = current_hash
            result = {
                'status': 'modified',
                'message': 'FICHIER MODIFIÉ !',
                'details': file_info
            }
        
        self._save_database()
        return result
    
    def check_all_files(self):
        """
        Vérifie l'intégrité de tous les fichiers surveillés.
        
        Returns:
            dict: Résultats de toutes les vérifications
        """
        results = {
            'intact': [],
            'modified': [],
            'missing': [],
            'errors': []
        }
        
        print(f"🔍 Vérification de {len(self.database)} fichiers...\n")
        
        for file_path in self.database:
            result = self.check_file(file_path)
            results[result['status']].append({
                'path': file_path,
                'result': result
            })
            
            # Affichage en temps réel
            status_icon = {
                'intact': '✅',
                'modified': '🚨',
                'missing': '❌',
                'error': '⚠️'
            }
            print(f"{status_icon.get(result['status'], '?')} {file_path}: {result['message']}")
        
        return results
    
    def add_directory(self, directory_path, recursive=True, algorithm='sha256', extensions=None):
        """
        Ajoute tous les fichiers d'un répertoire à la surveillance.
        
        Args:
            directory_path (str): Chemin vers le répertoire
            recursive (bool): Parcours récursif des sous-dossiers
            algorithm (str): Algorithme de hashing
            extensions (list): Liste d'extensions à inclure (None = toutes)
        
        Returns:
            int: Nombre de fichiers ajoutés
        """
        if not os.path.isdir(directory_path):
            print(f"❌ Le répertoire n'existe pas: {directory_path}")
            return 0
        
        added_count = 0
        path_obj = Path(directory_path)
        
        # Pattern de recherche selon le mode récursif
        pattern = "**/*" if recursive else "*"
        
        for file_path in path_obj.glob(pattern):
            if file_path.is_file():
                # Filtrer par extensions si spécifié
                if extensions and file_path.suffix.lower() not in extensions:
                    continue
                
                if self.add_file(str(file_path), algorithm):
                    added_count += 1
        
        print(f"📁 {added_count} fichiers ajoutés depuis {directory_path}")
        return added_count
    
    def remove_file(self, file_path):
        """
        Retire un fichier de la surveillance.
        
        Args:
            file_path (str): Chemin vers le fichier
        
        Returns:
            bool: True si retiré avec succès
        """
        if file_path in self.database:
            del self.database[file_path]
            if self._save_database():
                print(f"🗑️  Fichier retiré de la surveillance: {file_path}")
                return True
        else:
            print(f"❌ Fichier non surveillé: {file_path}")
        return False
    
    def list_files(self):
        """Affiche la liste des fichiers surveillés avec leur statut."""
        if not self.database:
            print("📋 Aucun fichier surveillé.")
            return
        
        print(f"📋 Fichiers surveillés ({len(self.database)}):")
        print("-" * 80)
        
        for file_path, info in self.database.items():
            status_icon = {
                'intact': '✅',
                'modified': '🚨',
                'missing': '❌'
            }.get(info.get('status', 'unknown'), '❓')
            
            print(f"{status_icon} {file_path}")
            print(f"   Algorithm: {info['algorithm'].upper()}")
            print(f"   Taille: {info['size']} bytes")
            print(f"   Ajouté: {info['added_date'][:19]}")
            print(f"   Dernière vérification: {info['last_check'][:19]}")
            print()
    
    def generate_report(self, output_file="integrity_report.txt"):
        """
        Génère un rapport détaillé de l'état d'intégrité.
        
        Args:
            output_file (str): Fichier de sortie pour le rapport
        """
        results = self.check_all_files()
        
        report_content = [
            f"RAPPORT D'INTÉGRITÉ DE FICHIERS",
            f"=" * 50,
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"RÉSUMÉ:",
            f"--------",
            f"• Fichiers intacts: {len(results['intact'])}",
            f"• Fichiers modifiés: {len(results['modified'])}",
            f"• Fichiers manquants: {len(results['missing'])}",
            f"• Erreurs: {len(results['errors'])}",
            f"",
        ]
        
        # Détails des fichiers modifiés
        if results['modified']:
            report_content.extend([
                "🚨 FICHIERS MODIFIÉS:",
                "-" * 30,
            ])
            for item in results['modified']:
                details = item['result']['details']
                report_content.extend([
                    f"Fichier: {item['path']}",
                    f"  Empreinte précédente: {details.get('previous_hash', 'N/A')}",
                    f"  Empreinte actuelle: {details.get('current_hash', 'N/A')}",
                    f"  Dernière vérification: {details['last_check'][:19]}",
                    ""
                ])
        
        # Détails des fichiers manquants
        if results['missing']:
            report_content.extend([
                "❌ FICHIERS MANQUANTS:",
                "-" * 30,
            ])
            for item in results['missing']:
                report_content.append(f"• {item['path']}")
            report_content.append("")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_content))
            print(f"📄 Rapport généré: {output_file}")
        except IOError as e:
            print(f"❌ Erreur génération rapport: {e}")


def main():
    """Fonction principale avec interface en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Vérificateur d'Intégrité de Fichiers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python file_integrity_checker.py add /path/to/file
  python file_integrity_checker.py add-dir /path/to/directory
  python file_integrity_checker.py check /path/to/file
  python file_integrity_checker.py check-all
  python file_integrity_checker.py list
  python file_integrity_checker.py report
        """
    )
    
    parser.add_argument('command', 
                       choices=['add', 'add-dir', 'check', 'check-all', 'remove', 'list', 'report'],
                       help='Commande à exécuter')
    
    parser.add_argument('path', nargs='?', 
                       help='Chemin du fichier ou répertoire')
    
    parser.add_argument('--algorithm', '-a', 
                       choices=['md5', 'sha1', 'sha256', 'sha512'],
                       default='sha256',
                       help='Algorithme de hashing (défaut: sha256)')
    
    parser.add_argument('--database', '-d',
                       default='integrity_database.json',
                       help='Fichier de base de données (défaut: integrity_database.json)')
    
    parser.add_argument('--recursive', '-r',
                       action='store_true',
                       help='Parcours récursif pour add-dir')
    
    parser.add_argument('--extensions', '-e',
                       nargs='+',
                       help='Extensions de fichiers à inclure (ex: .txt .py)')
    
    parser.add_argument('--output', '-o',
                       default='integrity_report.txt',
                       help='Fichier de sortie pour le rapport')
    
    args = parser.parse_args()
    
    # Initialisation du vérificateur
    checker = FileIntegrityChecker(args.database)
    
    print("🛡️  Vérificateur d'Intégrité de Fichiers v1.0")
    print("=" * 50)
    
    try:
        if args.command == 'add':
            if not args.path:
                print("❌ Chemin du fichier requis pour 'add'")
                sys.exit(1)
            checker.add_file(args.path, args.algorithm)
        
        elif args.command == 'add-dir':
            if not args.path:
                print("❌ Chemin du répertoire requis pour 'add-dir'")
                sys.exit(1)
            checker.add_directory(args.path, args.recursive, args.algorithm, args.extensions)
        
        elif args.command == 'check':
            if not args.path:
                print("❌ Chemin du fichier requis pour 'check'")
                sys.exit(1)
            result = checker.check_file(args.path)
            print(f"\n📊 Résultat: {result['message']}")
        
        elif args.command == 'check-all':
            checker.check_all_files()
        
        elif args.command == 'remove':
            if not args.path:
                print("❌ Chemin du fichier requis pour 'remove'")
                sys.exit(1)
            checker.remove_file(args.path)
        
        elif args.command == 'list':
            checker.list_files()
        
        elif args.command == 'report':
            checker.generate_report(args.output)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Opération interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
