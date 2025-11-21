#!/usr/bin/env python3
"""
Generate PWA icons from source image with nearest-neighbor scaling for pixel art.

This script generates all required icon sizes for PWA installation on iOS and Android:
- Standard PWA icons (192x192, 512x512)
- Apple Touch icons (180x180)
- Maskable icons for Android adaptive icons (192x192, 512x512)
- Favicons (16x16, 32x32, 48x48, favicon.ico)

For pixel art, it uses NEAREST resampling to keep pixels crisp.
"""

import os
from pathlib import Path
from PIL import Image

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
SOURCE_IMAGE = PROJECT_ROOT / "frontend/public/assets/images/cup.png"
OUTPUT_DIR = PROJECT_ROOT / "frontend/public"

# Icon sizes to generate
ICON_SIZES = {
    "icon-512.png": 512,
    "icon-192.png": 192,
    "apple-touch-icon.png": 180,
    "favicon-48x48.png": 48,
    "favicon-32x32.png": 32,
    "favicon-16x16.png": 16,
}

# Maskable icon sizes (with 20% safe zone)
MASKABLE_SIZES = {
    "icon-maskable-512.png": (512, 410),  # (output_size, content_size)
    "icon-maskable-192.png": (192, 154),  # 80% content, 20% safe zone
}


def make_square(img):
    """
    Make image square by centering it in a square canvas with transparent padding.

    For pixel art, we want to preserve the exact pixels without scaling,
    so we add transparent padding to make it square.

    Args:
        img: PIL Image object

    Returns:
        PIL Image object that is square
    """
    width, height = img.size

    # Already square
    if width == height:
        return img

    # Create square canvas with transparent background
    size = max(width, height)
    square_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))

    # Center the original image
    offset_x = (size - width) // 2
    offset_y = (size - height) // 2
    square_img.paste(img, (offset_x, offset_y))

    return square_img


def resize_nearest(img, size):
    """
    Resize image using nearest-neighbor algorithm to preserve pixel art.

    Args:
        img: PIL Image object
        size: Target size (single int for square output)

    Returns:
        Resized PIL Image object
    """
    return img.resize((size, size), Image.NEAREST)


def create_maskable(img, output_size, content_size):
    """
    Create maskable icon with safe zone for Android adaptive icons.

    Maskable icons need a 20% safe zone around the content to prevent
    cropping on different Android device shapes.

    Args:
        img: PIL Image object (should be square)
        output_size: Final icon size (e.g., 512)
        content_size: Size to scale content to (e.g., 410 for 80% of 512)

    Returns:
        PIL Image object with content centered and safe zone padding
    """
    # Resize content to fit in safe zone
    content = resize_nearest(img, content_size)

    # Create transparent canvas at output size
    maskable = Image.new('RGBA', (output_size, output_size), (0, 0, 0, 0))

    # Center the content
    offset = (output_size - content_size) // 2
    maskable.paste(content, (offset, offset))

    return maskable


def create_favicon_ico(favicon_images, output_path):
    """
    Create multi-resolution favicon.ico file.

    Args:
        favicon_images: List of PIL Image objects
        output_path: Path to save favicon.ico
    """
    # Sort by size (largest first works better for .ico)
    favicon_images.sort(key=lambda img: img.size[0], reverse=True)

    # Save as .ico with multiple sizes
    favicon_images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.size[0], img.size[1]) for img in favicon_images]
    )


def main():
    """
    Generate all PWA icons from source image.
    """
    print("PWA Icon Generator")
    print("=" * 50)

    # Check source image exists
    if not SOURCE_IMAGE.exists():
        print(f"ERROR: Source image not found: {SOURCE_IMAGE}")
        return

    # Load source image
    print(f"\nLoading source image: {SOURCE_IMAGE}")
    source = Image.open(SOURCE_IMAGE)
    print(f"Source size: {source.size[0]}x{source.size[1]}")
    print(f"Source mode: {source.mode}")

    # Convert to RGBA if needed (for transparency support)
    if source.mode != 'RGBA':
        print("Converting to RGBA...")
        source = source.convert('RGBA')

    # Make square
    print("\nMaking image square...")
    square_source = make_square(source)
    print(f"Square size: {square_source.size[0]}x{square_source.size[1]}")

    # Create output directory if needed
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate standard icons
    print("\nGenerating standard icons:")
    print("-" * 50)
    for filename, size in ICON_SIZES.items():
        output_path = OUTPUT_DIR / filename
        print(f"Creating {filename} ({size}x{size})...")

        icon = resize_nearest(square_source, size)
        icon.save(output_path, 'PNG')

        # Set permissions to 644
        os.chmod(output_path, 0o644)
        print(f"  Saved: {output_path}")

    # Generate maskable icons
    print("\nGenerating maskable icons:")
    print("-" * 50)
    for filename, (output_size, content_size) in MASKABLE_SIZES.items():
        output_path = OUTPUT_DIR / filename
        print(f"Creating {filename} ({output_size}x{output_size}, content: {content_size}x{content_size})...")

        maskable = create_maskable(square_source, output_size, content_size)
        maskable.save(output_path, 'PNG')

        # Set permissions to 644
        os.chmod(output_path, 0o644)
        print(f"  Saved: {output_path}")

    # Generate favicon.ico
    print("\nGenerating favicon.ico:")
    print("-" * 50)
    favicon_path = OUTPUT_DIR / "favicon.ico"
    print(f"Creating favicon.ico (multi-size: 16, 32, 48)...")

    # Load the individual favicon PNGs we just created
    favicon_images = [
        Image.open(OUTPUT_DIR / "favicon-16x16.png"),
        Image.open(OUTPUT_DIR / "favicon-32x32.png"),
        Image.open(OUTPUT_DIR / "favicon-48x48.png"),
    ]

    create_favicon_ico(favicon_images, favicon_path)
    os.chmod(favicon_path, 0o644)
    print(f"  Saved: {favicon_path}")

    # Summary
    print("\n" + "=" * 50)
    print("Icon generation complete!")
    print("=" * 50)
    print(f"\nGenerated {len(ICON_SIZES) + len(MASKABLE_SIZES) + 1} files:")
    print(f"  - {len(ICON_SIZES)} standard icons")
    print(f"  - {len(MASKABLE_SIZES)} maskable icons")
    print(f"  - 1 favicon.ico")
    print(f"\nAll icons saved to: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("  1. Verify icons in public/ folder")
    print("  2. Update vite.config.ts manifest (if needed)")
    print("  3. Rebuild frontend container")
    print("  4. Test in DevTools > Application > Manifest")


if __name__ == "__main__":
    main()
