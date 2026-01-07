from django.core.management.base import BaseCommand
from django.conf import settings
from login.models import Product, ProductImage
from utils.image_utils import generate_thumbnail


class Command(BaseCommand):
    help = 'Generate thumbnails for product images at common widths (300, 600, 900)'

    def add_arguments(self, parser):
        parser.add_argument('--widths', nargs='+', type=int, default=[300, 600, 900])

    def handle(self, *args, **options):
        widths = options['widths']
        self.stdout.write(self.style.NOTICE(f'Generating thumbnails for widths: {widths}'))

        # Process Product main images
        products = Product.objects.exclude(image='')
        total = products.count()
        self.stdout.write(f'Found {total} products with main images')
        for p in products:
            for w in widths:
                url = generate_thumbnail(p.image, w)
                self.stdout.write(f'Product {p.id}: generated {w} -> {url}')

        # Process ProductImage entries
        images = ProductImage.objects.all()
        self.stdout.write(f'Found {images.count()} ProductImage entries')
        for img in images:
            for w in widths:
                url = generate_thumbnail(img.image, w)
                self.stdout.write(f'ProductImage {img.id}: generated {w} -> {url}')

        self.stdout.write(self.style.SUCCESS('Thumbnail generation completed'))
