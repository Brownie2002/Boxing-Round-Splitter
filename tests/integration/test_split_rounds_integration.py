import unittest
import os
import subprocess
import tempfile
import shutil
from datetime import datetime
import json

class TestSplitRoundsIntegration(unittest.TestCase):
    """Tests d'intégration pour split_rounds.py avec un fichier vidéo réel"""

    @classmethod
    def setUpClass(cls):
        """Configuration avant tous les tests"""
        # Chemin vers le fichier vidéo de test
        cls.test_video = "VID_20990401_000000_test_10min.mp4"

        # Vérifier que le fichier existe
        if not os.path.exists(cls.test_video):
            raise FileNotFoundError(f"Fichier vidéo de test introuvable: {cls.test_video}")

        # Créer un répertoire temporaire pour les tests
        cls.test_dir = tempfile.mkdtemp(prefix="split_rounds_test_")
        cls.original_dir = os.getcwd()

        # Se déplacer dans le répertoire de test
        os.chdir(cls.test_dir)

        # Copier le fichier vidéo dans le répertoire de test
        shutil.copy2(cls.test_video, os.path.join(cls.test_dir, cls.test_video))

    def setUp(self):
        """Configuration avant chaque test"""
        # S'assurer que le répertoire de sortie n'existe pas
        output_dir = "2099-04-01-boxing"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def tearDown(self):
        """Nettoyage après chaque test"""
        # Supprimer les fichiers temporaires créés
        temp_dir = "temp"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        # Supprimer le répertoire de sortie
        output_dir = "2099-04-01-boxing"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def test_split_rounds_with_real_video(self):
        """Test l'intégration complète avec un fichier vidéo réel"""
        # Chemin vers le fichier vidéo dans le répertoire de test
        test_video = os.path.join(self.test_dir, "VID_20990401_000000_test_10min.mp4")

        # Exécuter le script de découpage
        result = subprocess.run([
            "python", os.path.join(self.original_dir, "src/core/split_rounds.py"),
            "--debug", test_video
        ], capture_output=True, text=True, cwd=self.test_dir)

        # Vérifier que le script s'exécute sans erreur
        self.assertEqual(result.returncode, 0, f"split_rounds.py a échoué: {result.stderr}")

        # Vérifier que le répertoire de sortie est créé
        output_dir = "2099-04-01-boxing"
        self.assertTrue(os.path.exists(output_dir), "Répertoire de sortie non créé")

        # Vérifier que les fichiers de sortie sont créés
        expected_files = [
            "2099-04-01_round_01.mp4",
            "2099-04-01_round_02.mp4",
            "bell_ringing_debug.txt"
        ]

        for expected_file in expected_files:
            full_path = os.path.join(output_dir, expected_file)
            self.assertTrue(os.path.exists(full_path), f"Fichier attendu non trouvé: {expected_file}")

        # Vérifier que le fichier de débogage contient les informations attendues
        debug_file = os.path.join(output_dir, "bell_ringing_debug.txt")
        with open(debug_file, 'r') as f:
            debug_content = f.read()

        # Vérifier que le fichier contient des événements de sonnerie de cloche
        self.assertIn("Événement", debug_content, "Aucun événement de sonnerie de cloche détecté")
        self.assertIn("Informations de Débogage de Détection de Sonnerie de Cloche", debug_content)

        # Vérifier les métadonnées des fichiers vidéo de sortie
        for round_num in [1, 2]:
            output_file = os.path.join(output_dir, f"2099-04-01_round_{round_num:02d}.mp4")
            self.assertTrue(os.path.exists(output_file), f"Fichier de round {round_num} non trouvé")

            # Vérifier que le fichier est un fichier vidéo valide
            self.assertGreater(os.path.getsize(output_file), 1024, f"Fichier de round {round_num} trop petit")

            # Vérifier les métadonnées avec FFprobe
            command = [
                'ffprobe',
                '-v', 'error',
                '-show_format',
                '-print_format', 'json',
                output_file
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            metadata = json.loads(result.stdout)

            # Vérifier que les métadonnées contiennent les informations attendues
            self.assertIn('format', metadata, "Métadonnées vidéo invalides")
            self.assertIn('duration', metadata['format'], "Durée manquante dans les métadonnées")

            # Vérifier que la durée est raisonnable pour un round (environ 2 minutes)
            duration = float(metadata['format']['duration'])
            self.assertGreater(duration, 100, f"Durée du round {round_num} trop courte: {duration}s")
            self.assertLess(duration, 150, f"Durée du round {round_num} trop longue: {duration}s")

    def test_multiple_videos_sorting(self):
        """Test le tri de plusieurs vidéos par date de création"""
        # Créer un fichier vidéo supplémentaire avec une date différente
        test_video2 = "VID_20990402_000000_test_10min.mp4"
        shutil.copy2(os.path.join(self.original_dir, "VID_20990401_000000_test_10min.mp4"),
                    os.path.join(self.test_dir, test_video2))

        # Exécuter le script avec plusieurs vidéos
        result = subprocess.run([
            "python", os.path.join(self.original_dir, "src/core/split_rounds.py"),
            "--debug", "VID_20990401_000000_test_10min.mp4", "VID_20990402_000000_test_10min.mp4"
        ], capture_output=True, text=True, cwd=self.test_dir)

        # Vérifier que le script s'exécute sans erreur
        self.assertEqual(result.returncode, 0, f"split_rounds.py a échoué avec plusieurs vidéos: {result.stderr}")

        # Vérifier que les deux répertoires de sortie sont créés
        for date in ["2099-04-01", "2099-04-02"]:
            output_dir = f"{date}-boxing"
            self.assertTrue(os.path.exists(output_dir), f"Répertoire de sortie {date} non créé")

    def test_logo_parameter(self):
        """Test le paramètre --logo"""
        # Utiliser le logo par défaut
        result = subprocess.run([
            "python", os.path.join(self.original_dir, "src/core/split_rounds.py"),
            "--debug", "--logo", os.path.join(self.original_dir, "src/core/logo.png"),
            "VID_20990401_000000_test_10min.mp4"
        ], capture_output=True, text=True, cwd=self.test_dir)

        # Vérifier que le script s'exécute sans erreur
        self.assertEqual(result.returncode, 0, f"split_rounds.py a échoué avec le logo: {result.stderr}")

        # Vérifier que les fichiers de sortie sont créés
        output_dir = "2099-04-01-boxing"
        self.assertTrue(os.path.exists(output_dir), "Répertoire de sortie non créé")

        # Vérifier que les fichiers vidéo contiennent le logo
        for round_num in [1, 2]:
            output_file = os.path.join(output_dir, f"2099-04-01_round_{round_num:02d}.mp4")
            self.assertTrue(os.path.exists(output_file), f"Fichier de round {round_num} non trouvé")

    @classmethod
    def tearDownClass(cls):
        """Nettoyage après tous les tests"""
        # Se déplacer dans le répertoire original
        os.chdir(cls.original_dir)

        # Supprimer le répertoire de test
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

if __name__ == '__main__':
    unittest.main()
