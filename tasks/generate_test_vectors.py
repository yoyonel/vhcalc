import numpy as np
from PIL import Image
import imagehash
import binascii

def imghash_to_bytes(imghash):
    bin_array_to_hex = str(imghash)
    return binascii.a2b_hex(bin_array_to_hex)

def generate_vectors():
    vectors = []

    # 1. All black
    img_black = Image.new('L', (32, 32), color=0)
    hash_black = imagehash.phash(img_black)
    vectors.append(("black", img_black, hash_black))

    # 2. All white
    img_white = Image.new('L', (32, 32), color=255)
    hash_white = imagehash.phash(img_white)
    vectors.append(("white", img_white, hash_white))

    # 3. Checkerboard
    data = np.zeros((32, 32), dtype=np.uint8)
    data[::2, ::2] = 255
    data[1::2, 1::2] = 255
    img_check = Image.fromarray(data)
    hash_check = imagehash.phash(img_check)
    vectors.append(("checkerboard", img_check, hash_check))

    # 4. Gradient
    data = np.arange(32*32, dtype=np.uint8).reshape((32, 32))
    # map to 0-255
    data = (data / (32*32) * 255).astype(np.uint8)
    img_grad = Image.fromarray(data)
    hash_grad = imagehash.phash(img_grad)
    vectors.append(("gradient", img_grad, hash_grad))

    # 5. Random
    np.random.seed(42)
    data = np.random.randint(0, 256, (32, 32), dtype=np.uint8)
    img_rand = Image.fromarray(data)
    hash_rand = imagehash.phash(img_rand)
    vectors.append(("random", img_rand, hash_rand))

    print("/* Auto-generated test vectors */")
    print("#include <stdint.h>")
    print("#include <stddef.h>")
    print("")
    print("typedef struct {")
    print("    const char* name;")
    print("    uint8_t image[32*32];")
    print("    uint64_t expected_hash;")
    print("} test_vector_t;")
    print("")
    print(f"#define NUM_VECTORS {len(vectors)}")
    print("")
    print("test_vector_t test_vectors[] = {")

    for name, img, h in vectors:
        # Get raw bytes
        raw = np.array(img).tobytes()
        # raw bytes as C array
        hex_bytes = ", ".join([f"0x{b:02x}" for b in raw])

        # hash as uint64
        # imagehash stores as boolean array or hex string.
        # str(h) gives hex string e.g. 'd500...'
        hash_hex = str(h)
        hash_val = int(hash_hex, 16)

        print(f"    {{")
        print(f"        .name = \"{name}\",")
        print(f"        .image = {{ {hex_bytes} }},")
        print(f"        .expected_hash = 0x{hash_val:016x}ULL")
        print(f"    }},")

    print("};")

if __name__ == "__main__":
    generate_vectors()
