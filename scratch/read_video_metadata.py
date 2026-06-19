import struct

def parse_mp4_duration(filepath):
    with open(filepath, 'rb') as f:
        # Search for 'mvhd' box
        data = f.read()
        idx = data.find(b'mvhd')
        if idx == -1:
            print("mvhd box not found")
            return None
        
        # mvhd header: version (1 byte), flags (3 bytes)
        # version 0 or 1 determines size of creation/modification times and timescale/duration.
        version = data[idx + 4]
        print(f"mvhd version: {version}")
        
        if version == 0:
            # 4 bytes creation time, 4 bytes modification time, 4 bytes timescale, 4 bytes duration
            timescale_offset = idx + 4 + 4 + 4 + 4
            timescale = struct.unpack('>I', data[timescale_offset : timescale_offset + 4])[0]
            duration = struct.unpack('>I', data[timescale_offset + 4 : timescale_offset + 8])[0]
        elif version == 1:
            # 8 bytes creation time, 8 bytes modification time, 4 bytes timescale, 8 bytes duration
            timescale_offset = idx + 4 + 4 + 8 + 8
            timescale = struct.unpack('>I', data[timescale_offset : timescale_offset + 4])[0]
            duration = struct.unpack('>Q', data[timescale_offset + 4 : timescale_offset + 12])[0]
        else:
            print(f"Unknown version: {version}")
            return None
            
        duration_sec = duration / timescale
        print(f"Timescale: {timescale}")
        print(f"Duration ticks: {duration}")
        print(f"Duration in seconds: {duration_sec:.2f}")
        return duration_sec

if __name__ == '__main__':
    parse_mp4_duration("E:/PropVista_Final/static/property.mp4")
