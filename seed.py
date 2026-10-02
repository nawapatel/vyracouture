"""
Seed script — Populates the fashion store with sample collections and products.
Run once: python seed.py
"""

import os
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

IST = timezone(timedelta(hours=5, minutes=30))

client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client[os.getenv('MONGO_DB_NAME', 'fashion_store')]  # explicit: fashion store's own DB

# ── Collections ──────────────────────────────────────────

collections = [
    {'name': 'Dresses', 'slug': 'dresses', 'description': 'Trendy dresses for every occasion', 'sort_order': 1, 'is_active': True, 'banner_image': '', 'created_at': datetime.now(IST)},
    {'name': 'Shrug Dresses', 'slug': 'shrug-dresses', 'description': 'Layered elegance with shrug dresses', 'sort_order': 2, 'is_active': True, 'created_at': datetime.now(IST)},
    {'name': 'Hand Embroidered', 'slug': 'hand-embroidered', 'description': 'Artisan hand embroidery meets modern style', 'sort_order': 3, 'is_active': True, 'created_at': datetime.now(IST)},
    {'name': 'Linen Collection', 'slug': 'linen-collection', 'description': 'Breathable linen for summer comfort', 'sort_order': 4, 'is_active': True, 'created_at': datetime.now(IST)},
    {'name': 'Pinafore Picks', 'slug': 'pinafore-picks', 'description': 'Classic pinafore styles reimagined', 'sort_order': 5, 'is_active': True, 'created_at': datetime.now(IST)},
    {'name': 'Luxe Looms', 'slug': 'luxe-looms', 'description': 'Premium linen, silk & tissue fabrics', 'sort_order': 6, 'is_active': True, 'created_at': datetime.now(IST)},
    {'name': 'Sale', 'slug': 'sale', 'description': 'Amazing deals up to 50% off', 'sort_order': 7, 'is_active': True, 'created_at': datetime.now(IST)},
]

# Placeholder images using placeholder service
def ph(w, h, color, text):
    return f"https://placehold.co/{w}x{h}/{color}/fff?text={text.replace(' ', '+')}"

# ── Products ─────────────────────────────────────────────

products = [
    # Dresses
    {'name': 'Petal Romance', 'slug': 'petal-romance', 'sale_price': 1590, 'original_price': 1990, 'collection_slug': 'dresses', 'fabric': 'Pure Linen', 'is_sale': True, 'is_new': True, 'is_featured': True,
     'images': [ph(600,800,'E8B4B8','Petal+Romance'), ph(600,800,'D4A0A6','Petal+Romance+2')],
     'sizes': ['XS','S','M','L','XL','XXL'], 'colors': ['#E8B4B8','#C9929A'], 'description': 'A dreamy floral print dress in pure linen. Features a flattering A-line silhouette with delicate petal patterns.', 'care_instructions': 'Hand wash cold. Line dry in shade. Do not bleach.', 'stock': 50, 'sold_count': 120, 'in_stock': True},

    {'name': 'Indigo Chic', 'slug': 'indigo-chic', 'sale_price': 1690, 'original_price': 1990, 'collection_slug': 'dresses', 'fabric': 'Linen Blend', 'is_sale': True, 'is_new': True, 'is_featured': True,
     'images': [ph(600,800,'3F51B5','Indigo+Chic'), ph(600,800,'303F9F','Indigo+Chic+2')],
     'sizes': ['XS','S','M','L','XL'], 'colors': ['#3F51B5','#283593'], 'description': 'Contemporary indigo dress with modern cut and breathable fabric.', 'care_instructions': 'Machine wash cold. Tumble dry low.', 'stock': 40, 'sold_count': 85, 'in_stock': True},

    {'name': 'Radiant Rose', 'slug': 'radiant-rose', 'sale_price': 1790, 'original_price': 2190, 'collection_slug': 'dresses', 'fabric': 'Pure Linen', 'is_sale': True, 'is_featured': True,
     'images': [ph(600,800,'F48FB1','Radiant+Rose'), ph(600,800,'EC407A','Radiant+Rose+2')],
     'sizes': ['S','M','L','XL','XXL'], 'colors': ['#F48FB1','#EC407A'], 'description': 'Bold rose-colored linen dress perfect for summer outings.', 'care_instructions': 'Hand wash recommended.', 'stock': 35, 'sold_count': 95, 'in_stock': True},

    {'name': 'Earthy Bloom', 'slug': 'earthy-bloom', 'sale_price': 1690, 'original_price': 1990, 'collection_slug': 'dresses', 'fabric': 'Cotton Linen', 'is_sale': True,
     'images': [ph(600,800,'8D6E63','Earthy+Bloom'), ph(600,800,'795548','Earthy+Bloom+2')],
     'sizes': ['XS','S','M','L','XL'], 'colors': ['#8D6E63','#6D4C41'], 'description': 'Warm earth-toned dress with beautiful bloom prints.', 'care_instructions': 'Machine wash gentle cycle.', 'stock': 45, 'sold_count': 67, 'in_stock': True},

    {'name': 'Honey Muse', 'slug': 'honey-muse', 'sale_price': 1690, 'original_price': 1990, 'collection_slug': 'dresses', 'fabric': 'Pure Linen', 'is_sale': True,
     'images': [ph(600,800,'FFB300','Honey+Muse'), ph(600,800,'FFA000','Honey+Muse+2')],
     'sizes': ['S','M','L','XL'], 'colors': ['#FFB300','#FFA000'], 'description': 'Warm honey-colored linen dress with a relaxed fit.', 'care_instructions': 'Hand wash cold. Dry in shade.', 'stock': 30, 'sold_count': 54, 'in_stock': True},

    {'name': 'Pink Linen Serenity', 'slug': 'pink-linen-serenity', 'sale_price': 2590, 'original_price': 2610, 'collection_slug': 'dresses', 'fabric': 'Premium Linen', 'is_sale': True, 'is_new': True,
     'images': [ph(600,800,'F8BBD0','Pink+Serenity'), ph(600,800,'F48FB1','Pink+Serenity+2')],
     'sizes': ['XS','S','M','L','XL'], 'colors': ['#F8BBD0','#F48FB1'], 'description': 'Premium linen dress in soft pink. Elegant drape and luxurious feel.', 'care_instructions': 'Dry clean recommended.', 'stock': 25, 'sold_count': 40, 'in_stock': True},

    {'name': 'Stripe Fusion', 'slug': 'stripe-fusion', 'sale_price': 1690, 'original_price': 1990, 'collection_slug': 'dresses', 'fabric': 'Linen Blend', 'is_sale': True,
     'images': [ph(600,800,'546E7A','Stripe+Fusion'), ph(600,800,'455A64','Stripe+Fusion+2')],
     'sizes': ['XS','S','M','L','XL','XXL'], 'colors': ['#546E7A','#37474F'], 'description': 'Modern striped linen dress with a fusion of classic and contemporary.', 'care_instructions': 'Machine wash cold.', 'stock': 55, 'sold_count': 78, 'in_stock': True},

    {'name': 'Flora Linen Kaftan', 'slug': 'flora-linen-kaftan', 'sale_price': 1690, 'original_price': 2090, 'collection_slug': 'dresses', 'fabric': 'Pure Linen', 'is_sale': True, 'is_new': True,
     'images': [ph(600,800,'66BB6A','Flora+Kaftan'), ph(600,800,'4CAF50','Flora+Kaftan+2')],
     'sizes': ['S','M','L','XL'], 'colors': ['#66BB6A','#43A047'], 'description': 'Flowing linen kaftan with beautiful floral prints.', 'care_instructions': 'Hand wash cold. Line dry.', 'stock': 30, 'sold_count': 42, 'in_stock': True},

    # Hand Embroidered
    {'name': 'Cottage Ivory', 'slug': 'cottage-ivory', 'sale_price': 1590, 'original_price': 1990, 'collection_slug': 'hand-embroidered', 'fabric': 'Cotton with Embroidery', 'is_sale': True, 'is_new': True, 'is_featured': True,
     'images': [ph(600,800,'FFFDE7','Cottage+Ivory'), ph(600,800,'FFF9C4','Cottage+Ivory+2')],
     'sizes': ['XS','S','M','L','XL'], 'colors': ['#FFFDE7','#FFF9C4'], 'description': 'Hand-embroidered ivory dress with cottage-core aesthetic.', 'care_instructions': 'Hand wash only. Do not wring.', 'stock': 20, 'sold_count': 88, 'in_stock': True},

    {'name': 'Mary Midi', 'slug': 'mary-midi', 'sale_price': 1690, 'original_price': 2190, 'collection_slug': 'hand-embroidered', 'fabric': 'Hand Embroidered Cotton', 'is_sale': True, 'is_featured': True,
     'images': [ph(600,800,'CE93D8','Mary+Midi'), ph(600,800,'BA68C8','Mary+Midi+2')],
     'sizes': ['S','M','L','XL'], 'colors': ['#CE93D8','#BA68C8'], 'description': 'Elegant midi dress with intricate hand embroidery.', 'care_instructions': 'Dry clean only.', 'stock': 15, 'sold_count': 65, 'in_stock': True},

    {'name': 'Crimson Allure', 'slug': 'crimson-allure', 'sale_price': 1590, 'original_price': 1990, 'collection_slug': 'hand-embroidered', 'fabric': 'Pure Cotton', 'is_sale': True,
     'images': [ph(600,800,'E53935','Crimson+Allure'), ph(600,800,'C62828','Crimson+Allure+2')],
     'sizes': ['XS','S','M','L','XL'], 'colors': ['#E53935','#C62828'], 'description': 'Stunning crimson dress with hand-embroidered floral motifs.', 'care_instructions': 'Hand wash in cold water.', 'stock': 25, 'sold_count': 72, 'in_stock': True},

    # Linen Collection
    {'name': 'Springtime Linen Glow', 'slug': 'springtime-linen-glow', 'sale_price': 2290, 'original_price': 2590, 'collection_slug': 'linen-collection', 'fabric': 'Premium Linen', 'is_sale': True, 'is_new': True, 'is_featured': True,
     'images': [ph(600,800,'A5D6A7','Springtime+Glow'), ph(600,800,'81C784','Springtime+Glow+2')],
     'sizes': ['S','M','L','XL','XXL'], 'colors': ['#A5D6A7','#81C784'], 'description': 'Premium linen dress that glows with spring energy. Lightweight and luxurious.', 'care_instructions': 'Hand wash or gentle machine wash.', 'stock': 40, 'sold_count': 110, 'in_stock': True},

    {'name': 'Linen Red Bloom', 'slug': 'linen-red-bloom', 'sale_price': 2290, 'original_price': 2590, 'collection_slug': 'linen-collection', 'fabric': 'Pure Linen', 'is_sale': True,
     'images': [ph(600,800,'EF5350','Red+Bloom'), ph(600,800,'E53935','Red+Bloom+2')],
     'sizes': ['XS','S','M','L','XL'], 'colors': ['#EF5350','#E53935'], 'description': 'Vibrant red linen dress with bloom print pattern.', 'care_instructions': 'Wash separately. Line dry.', 'stock': 35, 'sold_count': 88, 'in_stock': True},

    {'name': 'Linen Bloom Lane', 'slug': 'linen-bloom-lane', 'sale_price': 1990, 'original_price': 2290, 'collection_slug': 'linen-collection', 'fabric': 'Cotton Linen', 'is_sale': True,
     'images': [ph(600,800,'FFCC80','Bloom+Lane'), ph(600,800,'FFB74D','Bloom+Lane+2')],
     'sizes': ['S','M','L','XL'], 'colors': ['#FFCC80','#FFB74D'], 'description': 'Cheerful linen dress with bloom patterns on a warm canvas.', 'care_instructions': 'Machine wash cold. Tumble dry low.', 'stock': 45, 'sold_count': 62, 'in_stock': True},

    # Pinafore Picks
    {'name': 'Pinafore Poppy', 'slug': 'pinafore-poppy', 'sale_price': 2090, 'original_price': 2390, 'collection_slug': 'pinafore-picks', 'fabric': 'Linen Blend', 'is_sale': True, 'is_new': True,
     'images': [ph(600,800,'FF7043','Pinafore+Poppy'), ph(600,800,'F4511E','Pinafore+Poppy+2')],
     'sizes': ['XS','S','M','L','XL'], 'colors': ['#FF7043','#F4511E'], 'description': 'Classic pinafore in poppy red. Layer it over a tee or wear solo.', 'care_instructions': 'Machine wash gentle.', 'stock': 30, 'sold_count': 45, 'in_stock': True},

    {'name': 'Velvet Vermilion', 'slug': 'velvet-vermilion', 'sale_price': 1890, 'original_price': 2190, 'collection_slug': 'pinafore-picks', 'fabric': 'Velvet Blend', 'is_sale': True,
     'images': [ph(600,800,'D32F2F','Velvet+Vermilion'), ph(600,800,'C62828','Velvet+Vermilion+2')],
     'sizes': ['S','M','L','XL'], 'colors': ['#D32F2F','#C62828'], 'description': 'Luxurious velvet pinafore in deep vermilion.', 'care_instructions': 'Dry clean only.', 'stock': 20, 'sold_count': 38, 'in_stock': True},

    # Luxe Looms
    {'name': 'Gingham Grace', 'slug': 'gingham-grace', 'sale_price': 1990, 'original_price': 2290, 'collection_slug': 'luxe-looms', 'fabric': 'Premium Linen', 'is_sale': True, 'is_featured': True,
     'images': [ph(600,800,'90CAF9','Gingham+Grace'), ph(600,800,'64B5F6','Gingham+Grace+2')],
     'sizes': ['XS','S','M','L','XL'], 'colors': ['#90CAF9','#64B5F6'], 'description': 'Timeless gingham pattern in premium linen. Effortlessly chic.', 'care_instructions': 'Hand wash recommended.', 'stock': 35, 'sold_count': 72, 'in_stock': True},

    {'name': 'Lavender Garden', 'slug': 'lavender-garden', 'sale_price': 1890, 'original_price': 2290, 'collection_slug': 'luxe-looms', 'fabric': 'Silk Linen Blend', 'is_sale': True,
     'images': [ph(600,800,'CE93D8','Lavender+Garden'), ph(600,800,'BA68C8','Lavender+Garden+2')],
     'sizes': ['S','M','L','XL'], 'colors': ['#CE93D8','#BA68C8'], 'description': 'Silk-linen blend dress in soothing lavender with garden prints.', 'care_instructions': 'Dry clean recommended.', 'stock': 25, 'sold_count': 56, 'in_stock': True},

    {'name': 'Daisy Drizzle', 'slug': 'daisy-drizzle', 'sale_price': 1790, 'original_price': 2090, 'collection_slug': 'luxe-looms', 'fabric': 'Linen Silk', 'is_sale': True, 'is_new': True,
     'images': [ph(600,800,'FFF176','Daisy+Drizzle'), ph(600,800,'FFEE58','Daisy+Drizzle+2')],
     'sizes': ['XS','S','M','L'], 'colors': ['#FFF176','#FFEE58'], 'description': 'Playful daisy print on luxurious linen silk blend.', 'care_instructions': 'Hand wash cold. Lay flat to dry.', 'stock': 30, 'sold_count': 48, 'in_stock': True},

    # Men's / Unisex
    {'name': 'Linen Blue Petal Shirt', 'slug': 'linen-blue-petal-shirt', 'sale_price': 1290, 'original_price': 1690, 'collection_slug': 'linen-collection', 'fabric': 'Pure Linen', 'is_sale': True,
     'images': [ph(600,800,'42A5F5','Blue+Petal'), ph(600,800,'2196F3','Blue+Petal+2')],
     'sizes': ['S','M','L','XL','XXL'], 'colors': ['#42A5F5','#2196F3'], 'description': 'Relaxed-fit linen shirt in ocean blue.', 'care_instructions': 'Machine wash cold. Hang to dry.', 'stock': 60, 'sold_count': 92, 'in_stock': True},

    {'name': 'Linen Vanilla Shirt', 'slug': 'linen-vanilla-shirt', 'sale_price': 1290, 'original_price': 1690, 'collection_slug': 'linen-collection', 'fabric': 'Pure Linen', 'is_sale': True,
     'images': [ph(600,800,'FFF8E1','Vanilla+Shirt'), ph(600,800,'FFECB3','Vanilla+Shirt+2')],
     'sizes': ['S','M','L','XL','XXL'], 'colors': ['#FFF8E1','#FFECB3'], 'description': 'Classic vanilla linen shirt for everyday elegance.', 'care_instructions': 'Machine wash cold.', 'stock': 55, 'sold_count': 78, 'in_stock': True},

    # Sale items
    {'name': 'Fairy Rouge Linen', 'slug': 'fairy-rouge-linen', 'sale_price': 1190, 'original_price': 1770, 'collection_slug': 'sale', 'fabric': 'Linen Blend', 'is_sale': True,
     'images': [ph(600,800,'EF9A9A','Fairy+Rouge'), ph(600,800,'E57373','Fairy+Rouge+2')],
     'sizes': ['XS','S','M','L','XL'], 'colors': ['#EF9A9A','#E57373'], 'description': 'Beautiful rouge linen at an amazing sale price.', 'care_instructions': 'Hand wash cold.', 'stock': 40, 'sold_count': 115, 'in_stock': True},

    {'name': 'Marigold Garden', 'slug': 'marigold-garden', 'sale_price': 1090, 'original_price': 1860, 'collection_slug': 'sale', 'fabric': 'Pure Cotton', 'is_sale': True,
     'images': [ph(600,800,'FFA726','Marigold+Garden'), ph(600,800,'FB8C00','Marigold+Garden+2')],
     'sizes': ['S','M','L','XL'], 'colors': ['#FFA726','#FB8C00'], 'description': 'Vibrant marigold garden print. Massive discount!', 'care_instructions': 'Machine wash cold.', 'stock': 50, 'sold_count': 130, 'in_stock': True},

    {'name': 'Dark Romance', 'slug': 'dark-romance', 'sale_price': 1690, 'original_price': 1770, 'collection_slug': 'sale', 'fabric': 'Silk Blend', 'is_sale': True,
     'images': [ph(600,800,'5D4037','Dark+Romance'), ph(600,800,'4E342E','Dark+Romance+2')],
     'sizes': ['XS','S','M','L'], 'colors': ['#5D4037','#4E342E'], 'description': 'Moody dark romance print on luxurious silk blend.', 'care_instructions': 'Dry clean only.', 'stock': 20, 'sold_count': 67, 'in_stock': True},
]

# ── Run Seed ─────────────────────────────────────────────

if __name__ == '__main__':
    print("🗑️  Clearing existing data...")
    db.collections.drop()
    db.products.drop()

    print("📦 Inserting collections...")
    result = db.collections.insert_many(collections)
    print(f"   ✅ {len(result.inserted_ids)} collections inserted")

    print("👗 Inserting products...")
    result = db.products.insert_many(products)
    print(f"   ✅ {len(result.inserted_ids)} products inserted")

    print("\n🎉 Seed complete!")
    print(f"   Collections: {db.collections.count_documents({})}")
    print(f"   Products: {db.products.count_documents({})}")
