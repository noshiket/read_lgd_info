#!/usr/bin/env python3
"""
Read logo file (LGD) information and optionally export as PNG
Based on logo.h structure from Amatsukaze
"""

import struct
import sys
import argparse

def ycbcr_to_rgb(y, cb, cr):
    """Convert YCbCr to RGB (ITU-R BT.601)"""
    # Y: 0-4096, Cb/Cr: -2048-2048
    # Normalize to 0-255 range
    y_norm = y / 4096.0 * 255.0
    cb_norm = cb / 2048.0 * 128.0
    cr_norm = cr / 2048.0 * 128.0

    # ITU-R BT.601 conversion
    r = y_norm + 1.402 * cr_norm
    g = y_norm - 0.344136 * cb_norm - 0.714136 * cr_norm
    b = y_norm + 1.772 * cb_norm

    # Clamp to 0-255
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))

    return (r, g, b)

def read_lgd_info(filepath, output_png=None):
    """Read logo file header and pixel data"""
    with open(filepath, 'rb') as f:
        # Read LOGO_FILE_HEADER (28 bytes str + 4 bytes logonum = 32 bytes)
        file_header = f.read(32)
        header_str = file_header[0:28].decode('ascii', errors='ignore').rstrip('\x00')
        logonum = struct.unpack('>I', file_header[28:32])[0]  # Big Endian

        print(f"File Header: {header_str}")
        print(f"Logo count: {logonum}")
        print("")

        # Read LOGO_HEADER
        # struct: char name[32], short x, y, h, w, fi, fo, st, ed
        logo_header = f.read(48)  # 32 + 2*8 = 48 bytes

        # Parse header
        # Try UTF-8 first (used by logo_scanner), then fallback to Shift_JIS
        try:
            name = logo_header[0:32].decode('utf-8', errors='strict').rstrip('\x00')
        except UnicodeDecodeError:
            name = logo_header[0:32].decode('shift_jis', errors='ignore').rstrip('\x00')
        x, y, h, w, fi, fo, st, ed = struct.unpack('<hhhhhhhh', logo_header[32:48])

        pixel_data_offset = 32 + 48 + (w * h * 12)
        f.seek(pixel_data_offset)
        ext_header_bytes = f.read(540)
        service_id = "Unknown"
        if len(ext_header_bytes) >= 540:
            # Offset for serviceId: 40 (ints) + 256 (name + pad) = 296
            service_id = struct.unpack('<i', ext_header_bytes[296:300])[0]
        
        print(f"Logo File Information:")
        print(f"  Name: {name}")
        print(f"  Service ID: {service_id}")
        print(f"  Position (x, y): ({x}, {y})")
        print(f"  Size (w x h): {w} x {h}")
        print(f"")
        print(f"Command to create logo from TS:")
        print(f"  ./logo_scanner input.ts <serviceid> {x} {y} {w} {h} output.lgd")

        # Read pixel data if PNG output is requested
        if output_png:
            try:
                from PIL import Image
            except ImportError:
                print("\nError: PIL (Pillow) is required for PNG export.")
                print("Install with: pip3 install Pillow")
                return None

            # Read all LOGO_PIXEL data
            # Each LOGO_PIXEL: 6 shorts = 12 bytes
            pixel_count = h * w
            pixel_data = []

            for i in range(pixel_count):
                pixel_bytes = f.read(12)
                if len(pixel_bytes) < 12:
                    print(f"\nWarning: Incomplete pixel data at pixel {i}")
                    break

                # LOGO_PIXEL: dp_y, y, dp_cb, cb, dp_cr, cr (all short = 2 bytes)
                dp_y, y_val, dp_cb, cb_val, dp_cr, cr_val = struct.unpack('<hhhhhh', pixel_bytes)
                pixel_data.append({
                    'dp_y': dp_y,
                    'y': y_val,
                    'dp_cb': dp_cb,
                    'cb': cb_val,
                    'dp_cr': dp_cr,
                    'cr': cr_val
                })

            print(f"\nRead {len(pixel_data)} pixels")

            # Create PNG image
            # Create RGBA image (with alpha channel for transparency)
            f.seek(32 + 48)
            img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            pixels = img.load()

            for py in range(h):
                for px in range(w):
                    pixel_bytes = f.read(12)
                    if len(pixel_bytes) < 12: break
                    dp_y, y_val, dp_cb, cb_val, dp_cr, cr_val = struct.unpack('<hhhhhh', pixel_bytes)
                    
                    r, g, b = ycbcr_to_rgb(y_val, cb_val, cr_val)
                    # Alpha calculation based on Amatsukaze logic
                    alpha = int((dp_y + dp_cb + dp_cr) / 3000.0 * 255.0)
                    pixels[px, py] = (r, g, b, max(0, min(255, alpha)))

            img.save(output_png)
            print(f"\nPNG saved to: {output_png}")
            print(f"  - Size: {w} x {h} pixels")
            print(f"  - Format: RGBA (with alpha channel)")
            print(f"  - Alpha represents logo opacity")

        return {
            'name': name,
            'x': x,
            'y': y,
            'w': w,
            'h': h
        }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Read LGD logo file information and optionally export as PNG'
    )
    parser.add_argument('lgd_file', help='Input LGD logo file')
    parser.add_argument('-o', '--output', help='Output PNG file path')

    args = parser.parse_args()

    info = read_lgd_info(args.lgd_file, args.output)
