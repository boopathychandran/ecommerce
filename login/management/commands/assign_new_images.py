"""
Django management command to assign the newly downloaded images to products.
Maps the new image filenames to product names in the database.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from login.models import Product


class Command(BaseCommand):
    help = 'Assign downloaded images to products by matching product IDs'

    # Map product ID to new image filename
    PRODUCT_IMAGE_MAP = {
        # TV & Entertainment (IDs 1-5)
        1: "aura_x1_smart_tv.png",
        2: "aura_x2_smart_tv.png",
        3: "soundwave_surround.png",
        4: "streambox_pro.png",
        5: "projectmax_projector.png",
        
        # Smartphones (IDs 6-10)
        6: "zenphone_pro_12.png",
        7: "zenphone_lite_11.png",
        8: "zenphone_max.png",
        9: "omniphone_edge.png",
        10: "compactphone_mini.png",
        
        # Audio & Headphones (IDs 11-15)
        11: "nebula_air_earbuds.png",
        12: "nebula_pro_headphones.png",
        13: "basspower_speaker.png",
        14: "studiopro_earbuds.png",
        15: "soundbar_dolby.png",
        
        # Laptops (IDs 16-20)
        16: "falconbook_ultrabook.png",
        17: "falconbook_pro.png",
        18: "echobook_budget.png",
        19: "mobilemax_gaming.png",
        20: "thinbook_air.png",
        
        # Wearables & Fitness (IDs 21-24)
        21: "orbit_smartwatch_s3.png",
        22: "orbit_elite_smartwatch.png",
        23: "fitband_pro.png",
        24: "smartring_health.png",
        
        # Gaming (IDs 25-28)
        25: "glide_pro_keyboard.png",
        26: "velocity_x3_mouse.png",
        27: "gamepad_pro.png",
        28: "chairmax_gaming.png",
        
        # Cameras (IDs 29-31)
        29: "pixelpro_mirrorless.png",
        30: "snapmax_action.png",
        31: "instapro_dslr.png",
        
        # Home & Appliances (IDs 32-34)
        32: "homebreeze_purifier.png",
        33: "coolzone_ac.png",
        34: "warmplus_heater.png",
        
        # Accessories & Gadgets (IDs 35-37)
        35: "carryplus_backpack.png",
        36: "powerbank_ultra.png",
        37: "usbhub_pro.png",
        
        # Beauty & Personal Care (IDs 38-39)
        38: "freshglow_mirror.png",
        39: "beautyspa_hairdryer.png",
        
        # Sports & Outdoor (IDs 40-41)
        40: "prorun_shoes.png",
        41: "yogamat_premium.png",
    }

    def handle(self, *args, **options):
        images_dir = os.path.join(settings.MEDIA_ROOT, 'product_images')
        
        self.stdout.write('=' * 60)
        self.stdout.write('Assigning New Images to Products')
        self.stdout.write('=' * 60)
        
        updated_count = 0
        error_count = 0
        
        for product_id, image_filename in self.PRODUCT_IMAGE_MAP.items():
            try:
                product = Product.objects.get(id=product_id)
                image_path = os.path.join(images_dir, image_filename)
                
                if os.path.exists(image_path):
                    product.image = f'product_images/{image_filename}'
                    product.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'  [OK] ID {product_id}: {product.name} -> {image_filename}'
                    ))
                else:
                    error_count += 1
                    self.stdout.write(self.style.WARNING(
                        f'  [MISSING] ID {product_id}: Image not found: {image_filename}'
                    ))
            except Product.DoesNotExist:
                error_count += 1
                self.stdout.write(self.style.ERROR(
                    f'  [ERROR] Product ID {product_id} not found'
                ))
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count} products'))
        self.stdout.write(self.style.WARNING(f'Errors: {error_count}'))
        self.stdout.write('=' * 60)
