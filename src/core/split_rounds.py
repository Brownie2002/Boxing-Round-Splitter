import librosa
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
from datetime import timedelta
import subprocess
import os
import sys
import json
from datetime import datetime
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configure logging (default to INFO level)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create a temp directory if it doesn't exist
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

TEMP_WAV = os.path.join(TEMP_DIR, "temp_audio.wav")
TEMP_VIDEO_LIST = os.path.join(TEMP_DIR, "temp_video_list.txt")

# ========== PARAMÈTRES COURANTS (modifiables facilement) ==========
# Temps d'un round en secondes (modifiable couramment)
DEFAULT_ROUND_TIME = 120  # secondes

# ========== PARAMÈTRES EXPERTS (déconseillés à modifier) ==========
# Paramètres de détection de cloche - NE PAS MODIFIER SAUF SI VOUS SAVEZ CE QUE VOUS FAITES
DEFAULT_TARGET_FREQ = 2080  # Hz - Fréquence cible de la cloche
DEFAULT_BANDWIDTH = 50  # Hz - Bande passante autour de la fréquence cible
DEFAULT_MIN_PEAK_HEIGHT = 0.03  # Niveau minimal pour détecter un pic
DEFAULT_PEAKS_IN_ROW = 4  # Nombre minimal de pics consécutifs pour une détection
DEFAULT_MAX_GAP = 0.6  # Secondes maximales entre pics consécutifs

# Verrou pour la sortie console
console_lock = threading.Lock()

def validate_logo_path(logo_path):
    """
    Valide le chemin du fichier logo et le convertit en chemin absolu.

    Args:
        logo_path (str): Chemin vers le fichier logo (peut être relatif ou absolu).

    Returns:
        str: Chemin absolu vers le fichier logo si valide.

    Raises:
        FileNotFoundError: Si le fichier logo n'existe pas.
        ValueError: Si le fichier logo n'est pas un format d'image supporté.
    """
    if logo_path is None:
        return None

    # Convertir le chemin relatif en chemin absolu
    abs_logo_path = os.path.abspath(logo_path)

    # Vérifier si le fichier existe
    if not os.path.exists(abs_logo_path):
        raise FileNotFoundError(f"Fichier logo introuvable: {abs_logo_path}")

    # Vérifier si c'est un fichier (et non un dossier)
    if not os.path.isfile(abs_logo_path):
        raise ValueError(f"Le chemin du logo n'est pas un fichier: {abs_logo_path}")

    # Vérifier l'extension pour les formats d'image supportés
    supported_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
    file_ext = os.path.splitext(abs_logo_path)[1].lower()
    if file_ext not in supported_extensions:
        raise ValueError(f"Format de fichier logo non supporté: {file_ext}. Formats supportés: {', '.join(supported_extensions)}")

    logger.info(f"Utilisation du fichier logo: {abs_logo_path}")
    return abs_logo_path

def detect_bell_ringing(audio_path, output_debug_file=None, target_freq=DEFAULT_TARGET_FREQ,
                       bandwidth=DEFAULT_BANDWIDTH, min_peak_height=DEFAULT_MIN_PEAK_HEIGHT,
                       peaks_in_row=DEFAULT_PEAKS_IN_ROW, max_gap=DEFAULT_MAX_GAP):
    """
    Détecte les événements de sonnerie de cloche dans un fichier audio et retourne leurs timestamps.

    Détails supplémentaires dans /docs/design/bell_detection.md

    Args:
        audio_path (str): Chemin vers le fichier audio (format WAV).
        output_debug_file (str, optional): Chemin vers un fichier où les informations de débogage seront écrites.
        target_freq (float): Fréquence cible pour la détection de cloche (Hz).
        bandwidth (float): Bande passante autour de la fréquence cible (Hz).
        min_peak_height (float): Hauteur minimale de pic pour la détection.
        peaks_in_row (int): Nombre minimal de pics consécutifs pour une détection.
        max_gap (float): Gap maximal entre pics (secondes).

    Returns:
        list: Une liste de listes, où chaque sous-liste contient les timestamps d'un événement de sonnerie de cloche détecté.
    """
    # Charger l'audio avec librosa
    y, sr = librosa.load(audio_path, sr=None)

    # Créer un filtre passe-bande autour de target_freq
    low = (target_freq - bandwidth) / (sr / 2)
    high = (target_freq + bandwidth) / (sr / 2)
    b, a = butter(N=4, Wn=[low, high], btype='band')
    filtered_audio = filtfilt(b, a, y)

    # Calculer l'enveloppe d'amplitude
    amplitude = np.abs(filtered_audio)

    # Détecter les pics
    peaks, properties = find_peaks(amplitude, height=min_peak_height, distance=sr*0.1)

    # Convertir les indices de pics en temps en secondes
    peak_times = peaks / sr

    # Regrouper les pics en événements de sonnerie de cloche
    valid_events = []

    # Ne procéder que si nous avons des pics
    if len(peak_times) > 0:
        current_group = [peak_times[0]]

        for t in peak_times[1:]:
            if t - current_group[-1] <= max_gap:
                current_group.append(t)
            else:
                if len(current_group) >= peaks_in_row:
                    valid_events.append(current_group)
                current_group = [t]

        # Vérifier le dernier groupe
        if len(current_group) >= peaks_in_row:
            valid_events.append(current_group)

    # Écrire les informations de débogage si demandées
    if output_debug_file:
        with open(output_debug_file, 'w') as f:
            f.write("Informations de Débogage de Détection de Sonnerie de Cloche\n")
            f.write("=" * 40 + "\n")
            for i, group in enumerate(valid_events):
                # Convertir les timestamps en format hh:mm:ss.ssss
                formatted_times = [f"{int(t // 3600):02d}:{int((t % 3600) // 60):02d}:{int(t % 60):02d}.{int((t % 1) * 1000):03d}" for t in group]
                f.write(f"Événement {i+1}: {formatted_times}\n")
            f.write("=" * 40 + "\n")

    return valid_events

def get_video_creation_info(video_path):
    """
    Extrait les métadonnées de création d'un fichier vidéo en un seul appel FFprobe.

    Cette fonction optimisée récupère à la fois la date formatée (AAAA-MM-JJ) et
    l'objet datetime complet pour le tri, en un seul appel FFprobe.

    Args:
        video_path (str): Chemin vers le fichier vidéo.

    Returns:
        tuple: (formatted_date_str, datetime_obj) où:
            - formatted_date_str: Date de création au format 'AAAA-MM-JJ' ou 'Non disponible'
            - datetime_obj: Objet datetime complet ou None si non disponible

    Exemple:
        >>> formatted_date, datetime_obj = get_video_creation_info("video.mp4")
        >>> print(f"Date: {formatted_date}, Full datetime: {datetime_obj}")
    """
    try:
        # Appel unique à FFprobe pour obtenir toutes les métadonnées
        command = [
            'ffprobe',
            '-v', 'error',
            '-show_format',
            '-print_format', 'json',
            video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        metadata = json.loads(result.stdout)

        creation_time = metadata['format'].get('tags', {}).get('creation_time', None)

        if creation_time:
            datetime_obj = datetime.strptime(creation_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_date = datetime_obj.strftime('%Y-%m-%d')
            return formatted_date, datetime_obj
        else:
            return 'Non disponible', None

    except Exception as e:
        logger.warning(f"Impossible d'extraire les métadonnées de {video_path}: {e}")
        return f"Une erreur s'est produite: {e}", None

def get_video_metadata(video_path):
    """
    Extrait les métadonnées du fichier vidéo, y compris la date de création.

    Cette fonction utilise FFprobe pour récupérer les métadonnées vidéo au format JSON et extrait
    la date de création si disponible. La date de création est analysée et formatée en AAAA-MM-JJ.

    Args:
        video_path (str): Chemin vers le fichier vidéo.

    Returns:
        str: La date de création de la vidéo au format 'AAAA-MM-JJ' si disponible.
             Retourne 'Non disponible' si la date de création ne peut pas être extraite.
             Retourne un message d'erreur si une exception se produit pendant le traitement.

    Exemple:
        >>> creation_date = get_video_metadata("chemin/vers/video.mp4")
        >>> print(f"Date de création: {creation_date}")
        Date de création: 2026-02-15

    Note:
        Cette fonction nécessite que FFprobe soit installé et disponible dans le PATH système.
        La date de création est extraite de la balise 'creation_time' dans les métadonnées vidéo.
    """
    # Utiliser la fonction optimisée et retourner uniquement la date formatée
    formatted_date, _ = get_video_creation_info(video_path)
    return formatted_date

def sort_videos_by_creation_date(video_files):
    """
    Trie une liste de fichiers vidéo par leur date de création et retourne la liste triée avec la date de la première vidéo.

    Cette fonction optimisée extrait les métadonnées une seule fois par vidéo et retourne à la fois la liste triée
    et la date de création de la première vidéo pour le nommage du répertoire de sortie.

    Args:
        video_files (list): Liste des chemins des fichiers vidéo.

    Returns:
        tuple: (sorted_video_files, first_video_date, sorted_video_info) où:
            - sorted_video_files: Liste des chemins des vidéos triés par date de création (du plus ancien au plus récent)
            - first_video_date: Date de création de la première vidéo au format 'AAAA-MM-JJ'
            - sorted_video_info: Liste de tuples (video_path, formatted_date, datetime_obj) pour l'affichage

    Exemple:
        >>> sorted_videos, first_date, video_info = sort_videos_by_creation_date(video_files)
        >>> print(f"Première date vidéo: {first_date}")
        >>> for video, date, _ in video_info:
        ...     print(f"{video}: {date}")
    """
    # Obtenir les informations de création pour toutes les vidéos en une seule passe
    video_info = []
    for video in video_files:
        formatted_date, creation_datetime = get_video_creation_info(video)
        video_info.append((video, formatted_date, creation_datetime))

    # Trier par datetime de création (du plus ancien au plus récent), les vidéos sans date vont à la fin
    sorted_videos = sorted(
        video_info,
        key=lambda x: (x[2] is None, x[2] if x[2] else datetime.max)
    )

    # Extraire les chemins des vidéos triés
    sorted_video_files = [video for video, _, _ in sorted_videos]

    # Obtenir la date formatée de la première vidéo pour le nom du répertoire de sortie
    first_video_date = sorted_videos[0][1] if sorted_videos else 'Non disponible'

    return sorted_video_files, first_video_date, sorted_videos

def create_round_video(round_params, logo_path, temp_video_list, round_time):
    """
    Crée un fichier vidéo pour un round spécifique.

    Args:
        round_params (tuple): Tuple contenant (round_number, start_time, delta_sec, creation_date)
        logo_path (str): Chemin vers le fichier logo
        temp_video_list (str): Chemin vers le fichier de liste vidéo temporaire
        round_time (int): Durée d'un round en secondes

    Returns:
        str: Message de résultat
    """
    round_number, start_time, delta_sec, creation_date = round_params

    # Nom de fichier de sortie
    output_file = os.path.join(f"{creation_date}-boxing", f"{creation_date}_round_{round_number:02d}.mp4")

    cmd = [
        "nice", "-n", "10",
        "ffmpeg", "-y",
        "-ss", f"{max(0, start_time):.3f}",
        "-t", f"{delta_sec:.3f}",
        "-f", "concat", "-safe", "0",
        "-i", temp_video_list,
        "-i", logo_path,
        "-filter_complex",
        (
            "[0:v]drawtext=text='{}':"
            "fontsize=24:x=10:y=10:fontcolor=white:box=1:boxcolor=black@0.5[text];"
            "[text][1:v]overlay=W-w-10:10[outv]"
        ).format(creation_date),
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:a", "aac", "-b:a", "48k",
        "-c:v", "libx264",
        "-b:v", "4M",
        "-preset", "fast",
        "-movflags",  "+faststart",
        output_file,
    ]

    # Exécuter la commande ffmpeg
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Afficher le résultat avec verrouillage pour éviter les mélanges de sortie
    with console_lock:
        if result.returncode == 0:
            td = timedelta(seconds=start_time)
            hh_mm_ss = str(td).split(".")[0]
            delta_td = timedelta(seconds=delta_sec)
            delta_str = str(delta_td).split(".")[0].rjust(8, "0")
            logger.info(f"Création du round {round_number}: {output_file} ({hh_mm_ss} pour {delta_str})")
        else:
            logger.error(f"Échec de la création du round {round_number}: {output_file}")
            logger.debug("FFmpeg stdout: %s", result.stdout)
            logger.debug("FFmpeg stderr: %s", result.stderr)

    return output_file

def main():
    # Analyser les arguments de la ligne de commande
    parser = argparse.ArgumentParser(description='Découpe les vidéos de boxe en rounds individuels basés sur les sons de cloche.')

    # Paramètres courants
    parser.add_argument('video_files', nargs='+', help='Chemin(s) vers le(s) fichier(s) vidéo à traiter')
    parser.add_argument('--debug', action='store_true', help='Activer le logging de débogage')
    parser.add_argument('--logo', type=str, help='Chemin vers le fichier logo à superposer sur les vidéos de sortie', default=None)
    parser.add_argument('--round-time', type=int, help='Durée d\'un round en secondes (par défaut: 120)', default=DEFAULT_ROUND_TIME)
    parser.add_argument('--max-workers', type=int, help='Nombre maximum de threads pour le traitement parallèle (par défaut: 4)', default=4)

    # Paramètres experts (groupés sous un groupe d'options)
    expert_group = parser.add_argument_group('Paramètres experts (utiliser avec prudence)')
    expert_group.add_argument('--target-freq', type=int, help='Fréquence cible pour la détection de cloche (par défaut: 2080)', default=DEFAULT_TARGET_FREQ)
    expert_group.add_argument('--bandwidth', type=int, help='Bande passante autour de la fréquence cible (par défaut: 50)', default=DEFAULT_BANDWIDTH)
    expert_group.add_argument('--min-peak-height', type=float, help='Hauteur minimale de pic pour la détection (par défaut: 0.03)', default=DEFAULT_MIN_PEAK_HEIGHT)
    expert_group.add_argument('--peaks-in-row', type=int, help='Nombre minimal de pics consécutifs pour la détection (par défaut: 4)', default=DEFAULT_PEAKS_IN_ROW)
    expert_group.add_argument('--max-gap', type=float, help='Gap maximal entre pics (par défaut: 0.6)', default=DEFAULT_MAX_GAP)

    args = parser.parse_args()

    # Configurer le logging en fonction de l'option debug
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger.setLevel(log_level)

    # Obtenir les fichiers vidéo depuis les arguments de la ligne de commande
    video_files = args.video_files

    # Trier les vidéos par date de création et obtenir la date de la première vidéo en un seul appel
    sorted_video_files, creation_date, sorted_video_info = sort_videos_by_creation_date(video_files)

    if len(sorted_video_files) != len(video_files) or any(
        sorted_video_files[i] != video_files[i]
        for i in range(len(video_files))
    ):
        logger.info("Vidéos triées par date de création:")
        for i, (video, formatted_date, _) in enumerate(sorted_video_info, 1):
            date_str = formatted_date if formatted_date and formatted_date != 'Non disponible' else 'Inconnu'
            logger.info(f"  {i}. {os.path.basename(video)} - {date_str}")

    # Gérer le paramètre logo - s'assurer que nous avons toujours un logo
    if args.logo:
        try:
            logo_path = validate_logo_path(args.logo)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Erreur de logo: {e}")
            sys.exit(1)
    else:
        # Utiliser le logo par défaut si aucun logo n'est spécifié
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "logo.png")

        if not os.path.exists(logo_path):
            logger.error(f"Logo par défaut introuvable à: {logo_path}")
            sys.exit(1)

        logger.info(f"Utilisation du logo par défaut: {logo_path}")

    # Afficher les paramètres experts utilisés
    logger.info("Paramètres de détection de cloche:")
    logger.info(f"  Fréquence cible: {args.target_freq} Hz")
    logger.info(f"  Bande passante: {args.bandwidth} Hz")
    logger.info(f"  Hauteur minimale de pic: {args.min_peak_height}")
    logger.info(f"  Pics consécutifs: {args.peaks_in_row}")
    logger.info(f"  Gap maximal: {args.max_gap} secondes")

    logger.info(f"Date de création: {creation_date}")
    logger.info(f"Durée du round: {args.round_time} secondes")
    logger.info(f"Nombre maximum de workers: {args.max_workers}")

    # Créer temp_video_list.txt avec des chemins absolus (en utilisant les vidéos triées)
    with open(TEMP_VIDEO_LIST, "w") as f:
        for video in sorted_video_files:
            # Convertir les chemins relatifs en chemins absolus
            abs_video_path = os.path.abspath(video)
            f.write(f"file '{abs_video_path}'\n")

    # Étape 1: Extraire l'audio de la vidéo .lrv en utilisant ffmpeg
    logger.info("Extraction de l'audio avec ffmpeg vers %s", TEMP_WAV)
    ffmpeg_cmd = [
        "ffmpeg", "-v", "debug", "-y",  "-f", "concat", "-safe", "0",
        "-i", TEMP_VIDEO_LIST, "-vn",      # pas de vidéo
        "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", TEMP_WAV
    ]
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    logger.debug("FFmpeg stdout: %s", result.stdout)
    logger.debug("FFmpeg stderr: %s", result.stderr)

    # Étape 2: Détecter les événements de sonnerie de cloche
    logger.info("Détection des événements de sonnerie de cloche...")
    bell_ringing_file = os.path.join(TEMP_DIR, "bell_ringing_debug.txt")
    valid_events = detect_bell_ringing(
        TEMP_WAV,
        bell_ringing_file,
        target_freq=args.target_freq,
        bandwidth=args.bandwidth,
        min_peak_height=args.min_peak_height,
        peaks_in_row=args.peaks_in_row,
        max_gap=args.max_gap
    )
    logger.info("Informations de débogage écrites dans %s", bell_ringing_file)

    # Préparer les paramètres pour la création des rounds
    round_params_list = []
    round = 0

    for i, group in enumerate(valid_events):
        start_time = group[0] - 0.5

        # Regarder en avant pour le prochain groupe
        if i + 1 < len(valid_events):
            next_start = valid_events[i + 1][0]
            delta_sec = next_start - start_time + 1

            # Vérifier si delta est d'environ 2 minutes +- 2 secondes
            if args.round_time - 2 <= delta_sec <= args.round_time + 2:
                round += 1
                round_params_list.append((round, start_time, delta_sec, creation_date))

    # Créer le répertoire de sortie
    output_dir = f"{creation_date}-boxing"
    os.makedirs(output_dir, exist_ok=True)

    # Étape 3: Créer les vidéos des rounds en parallèle
    logger.info(f"Création de {len(round_params_list)} rounds en parallèle avec {args.max_workers} workers...")

    # Utiliser ThreadPoolExecutor pour le traitement parallèle
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # Soumettre toutes les tâches
        futures = []
        for params in round_params_list:
            future = executor.submit(
                create_round_video,
                params,
                logo_path,
                TEMP_VIDEO_LIST,
                args.round_time
            )
            futures.append(future)

        # Attendre la fin de toutes les tâches et collecter les résultats
        for future in as_completed(futures):
            try:
                result = future.result()
                # Le résultat est déjà journalisé dans la fonction create_round_video
            except Exception as e:
                logger.error(f"Erreur lors de la création d'un round: {e}")

    # Afficher les événements qui n'ont pas de groupe suivant
    for i, group in enumerate(valid_events):
        start_time = group[0] - 0.5
        td = timedelta(seconds=start_time)
        hh_mm_ss = str(td).split(".")[0]

        # Vérifier si cet événement a été traité (a un groupe suivant)
        if i + 1 >= len(valid_events):
            delta_str = "N/A (dernier groupe)"
            logger.info(f"Événement {i+1:<6} n'a pas de groupe suivant: {hh_mm_ss:<12} {delta_str:<15}")

if __name__ == "__main__":
    main()
