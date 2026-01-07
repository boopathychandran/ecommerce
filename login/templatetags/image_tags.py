from django import template
from django.conf import settings
from django.templatetags.static import static
from utils.image_utils import generate_thumbnail

register = template.Library()


@register.filter
def thumbnail(image_field, width=400):
    """Return thumbnail URL for given ImageFieldFile and width.
    If thumbnail cannot be generated, return original image URL or a default static image.
    Usage: {{ product.image|thumbnail:400 }}
    """
    if not image_field:
        return static('images/default.jpg')

    try:
        url = generate_thumbnail(image_field, width)
        if url:
            return url
    except Exception:
        pass

    # Fallbacks
    try:
        return image_field.url
    except Exception:
        return static('images/default.jpg')
