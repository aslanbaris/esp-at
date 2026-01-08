import struct
import argparse
import os

# Magic: "UPDT" (0x55504454)
MAGIC = 0x55504454

def pack_files(output_file, items):
    """
    Pack multiple files into a single binary with a simple header.
    Header Format:
      Magic (4 bytes)
      Count (4 bytes)
    Item Header Format:
      Label (16 bytes, null-padded)
      Size (4 bytes)
      Offset (4 bytes) - 0 for auto-lookup
      Type (4 bytes) - 0=App, 1=Data
    """
    
    with open(output_file, 'wb') as out_f:
        # Write Global Header
        out_f.write(struct.pack('<II', MAGIC, len(items)))
        
        for item in items:
            label, filepath, type_val = item
            
            if not os.path.exists(filepath):
                print(f"Error: File not found: {filepath}")
                return False
                
            size = os.path.getsize(filepath)
            
            # Write Item Header
            # Label (16s), Size (I), Offset (I), Type (I)
            # We use offset 0 to properly signify "lookup by label" logic in firmware
            header_data = struct.pack('<16sIII', label.encode('utf-8'), size, 0, type_val)
            out_f.write(header_data)
            
            # Write Item Data
            with open(filepath, 'rb') as in_f:
                while True:
                    chunk = in_f.read(4096)
                    if not chunk:
                        break
                    out_f.write(chunk)
            
            print(f"Packed '{label}': {filepath} ({size} bytes)")
            
    print(f"Successfully created {output_file}")
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pack firmware binaries into a single update package.')
    parser.add_argument('--out', default='build/update_package.bin', help='Output package file')
    
    # We expect these files to exist in the build directory usually
    parser.add_argument('--app', default='build/esp-at.bin', help='Application binary')
    parser.add_argument('--nvs', default='build/customized_partitions/mfg_nvs.bin', help='NVS binary')
    parser.add_argument('--fatfs', default='build/customized_partitions/fatfs.bin', help='FATFS binary')
    
    args = parser.parse_args()
    
    # Define items to pack: (Label, Path, Type 0=App/1=Data)
    items_to_pack = [
        ("mfg_nvs", args.nvs, 1),
        ("fatfs", args.fatfs, 1),
        ("app", args.app, 0)
    ]
    
    pack_files(args.out, items_to_pack)
