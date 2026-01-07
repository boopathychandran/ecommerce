from django.conf import settings


class ThumbnailsCacheControlMiddleware:
    """Add Cache-Control headers for generated thumbnails under MEDIA_URL/thumbnails/."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.media_prefix = getattr(settings, 'MEDIA_URL', '/media/')
        # ensure trailing slash
        if not self.media_prefix.endswith('/'):
            self.media_prefix += '/'
        self.thumb_prefix = self.media_prefix + 'thumbnails/'
        self.max_age = getattr(settings, 'THUMBNAILS_CACHE_MAX_AGE', 31536000)  # 1 year default

    def __call__(self, request):
        response = self.get_response(request)
        try:
            path = request.path
        except Exception:
            return response

        if path.startswith(self.thumb_prefix):
            # Only set if not already present
            if 'Cache-Control' not in response:
                response['Cache-Control'] = f'public, max-age={self.max_age}, immutable'
        return response
