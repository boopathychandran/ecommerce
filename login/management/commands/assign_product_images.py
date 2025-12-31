"""
Django management command to automatically assign images to products based on their names.
This reads all products and matches them with existing images in the product_images folder.
"""
import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from login.models import Product


class Command(BaseCommand):
    help = 'Automatically assign images to products based on product names'

    def normalize_name(self, name):
        """Convert product name to a normalized filename format"""
        # Convert to lowercase
        name = name.lower()
        # Replace special characters and spaces with underscores
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', '_', name)
        # Remove common size/spec suffixes for broader matching
        return name.strip('_')

    def find_best_match(self, product_name, image_files):
        """Find the best matching image file for a product name"""
        normalized_name = self.normalize_name(product_name)
        
        # Direct match first
        for img in image_files:
            img_name = os.path.splitext(img)[0].lower()
            if normalized_name == img_name or img_name.startswith(normalized_name[:20]):
                return img
        
        # Partial match - check if significant parts of the name match
        name_parts = normalized_name.split('_')
        for img in image_files:
            img_name = os.path.splitext(img)[0].lower()
            # Count matching parts
            matching_parts = sum(1 for part in name_parts if part and len(part) > 2 and part in img_name)
            if matching_parts >= 2:  # At least 2 significant parts match
                return img
        
        return None

    def handle(self, *args, **options):
        # Get all image files in the product_images folder
        images_dir = os.path.join(settings.MEDIA_ROOT, 'product_images')
        
        if not os.path.exists(images_dir):
            self.stdout.write(self.style.ERROR(f'Images directory not found: {images_dir}'))
            return
        
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))]
        
        self.stdout.write(f'Found {len(image_files)} image files in {images_dir}')
        
        # Get all products
        products = Product.objects.all()
        self.stdout.write(f'Found {products.count()} products')
        
        updated_count = 0
        skipped_count = 0
        not_found_count = 0
        not_found_products = []
        
        for product in products:
            # Skip if product already has an image
            if product.image:
                skipped_count += 1
                self.stdout.write(f'  [SKIP] {product.name} - already has image: {product.image}')
                continue
            
            # Find matching image
            matching_image = self.find_best_match(product.name, image_files)
            
            if matching_image:
                product.image = f'product_images/{matching_image}'
                product.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [OK] {product.name} -> {matching_image}'))
            else:
                not_found_count += 1
                not_found_products.append(product.name)
                self.stdout.write(self.style.WARNING(f'  [MISSING] {product.name} - no matching image found'))
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count} products'))
        self.stdout.write(f'Skipped (already had images): {skipped_count} products')
        self.stdout.write(self.style.WARNING(f'Missing images: {not_found_count} products'))
        
        if not_found_products:
            self.stdout.write('\nProducts needing images:')
            for name in not_found_products:
                self.stdout.write(f'  - {name}')
