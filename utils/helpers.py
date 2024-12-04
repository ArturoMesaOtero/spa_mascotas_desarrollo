import os


def get_valid_video_path(raza: str) -> str:
    """
    Válida y retorna la ruta correcta del video según la raza.
    """
    if not raza:
        return "./videos/mestizo.mp4"

    #raza_formato = raza.lower().replace(' ', '_')
    video_path = f"./videos/{raza}"

    return video_path if os.path.exists(video_path) else "./videos/mestizo.mp4"


def video_exists(path: str) -> bool:
    """
    Verifica si existe un video en la ruta especificada.
    """
    return os.path.exists(path) and path.endswith('.mp4')