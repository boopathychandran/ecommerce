import os
from io import BytesIO
from PIL import Image
from django.conf import settings


def generate_thumbnail(image_field, width):
    """
    Generate a thumbnail for the given ImageFieldFile at the requested width (px).
    Thumbnails are stored under MEDIA_ROOT/thumbnails/<width>/<original_path>.
    Returns the relative URL path (MEDIA_URL + thumbnail_relative_path) on success,
    or the original image url if generation fails.
    """
    if not image_field:
        return None

    try:
        # Ensure width is int
        width = int(width)
    except Exception:
        return image_field.url if hasattr(image_field, 'url') else None

    original_name = image_field.name  # e.g. product_images/abc.jpg
    if not original_name:
        return None

    # Build thumbnail relative path: thumbnails/<width>/<original_name>
    thumb_rel_path = os.path.join('thumbnails', str(width), original_name).replace('\\', '/')
    thumb_full_path = os.path.join(settings.MEDIA_ROOT, thumb_rel_path)

    # If thumbnail already exists, return its URL
    if os.path.exists(thumb_full_path):
        return settings.MEDIA_URL + thumb_rel_path

    # Create directories
    thumb_dir = os.path.dirname(thumb_full_path)
    os.makedirs(thumb_dir, exist_ok=True)

    original_full_path = os.path.join(settings.MEDIA_ROOT, original_name)
    if not os.path.exists(original_full_path):
        return settings.MEDIA_URL + original_name if hasattr(image_field, 'url') else None

    try:
        with Image.open(original_full_path) as img:
            # Preserve aspect ratio; fit into (width, width)
            img.convert('RGB')
            img.thumbnail((width, width), Image.LANCZOS)

            # Choose output format based on original extension
            ext = os.path.splitext(original_full_path)[1].lower()
            format = 'JPEG'
            save_kwargs = {'quality': 85, 'optimize': True}
            if ext in ['.png']:
                format = 'PNG'
                save_kwargs.pop('quality', None)

            # Save thumbnail
            img.save(thumb_full_path, format=format, **save_kwargs)

        return settings.MEDIA_URL + thumb_rel_path
    except Exception:
        # On failure, fall back to original url
        return settings.MEDIA_URL + original_name
