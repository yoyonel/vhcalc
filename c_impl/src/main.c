#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <stdint.h>
#include <inttypes.h>

#include "imghash.h"
#include "config.h"
#include "video_reader.h"

// Helper to write uint64 as Big Endian bytes
void write_hash_binary(uint64_t hash, FILE *out) {
    uint8_t bytes[8];
    for (int i = 0; i < 8; i++) {
        bytes[i] = (hash >> (56 - i * 8)) & 0xFF;
    }
    fwrite(bytes, 1, 8, out);
}

// Helper to print uint64 as hex string
void print_hash_hex(uint64_t hash, FILE *out) {
    fprintf(out, "%016" PRIx64, hash);
}

// Convert 8 bytes Big Endian to uint64
uint64_t bytes_to_uint64(const uint8_t *bytes) {
    uint64_t hash = 0;
    for (int i = 0; i < 8; i++) {
        hash |= ((uint64_t)bytes[i] << (56 - i * 8));
    }
    return hash;
}

static struct option long_options[] = {
    {"image-hashing-method", required_argument, 0, 'm'},
    {"decompress", no_argument, 0, 'd'},
    {"help", no_argument, 0, 'h'},
    {"version", no_argument, 0, 'v'},
    {0, 0, 0, 0}
};

void print_usage(const char *prog_name) {
    printf("Usage: %s [OPTIONS] [INPUT_STREAM]\n", prog_name);
    printf("Options:\n");
    printf("  -m, --image-hashing-method METHOD  The image hashing method to use (default: PerceptualHashing).\n");
    printf("  -d, --decompress                   Decompress images hashes from binary streams.\n");
    printf("  -h, --help                         Show this message and exit.\n");
    printf("  -v, --version                      Show version.\n");
}

int main(int argc, char *argv[]) {
    int opt;
    int decompress = 0;
    // const char *method = "PerceptualHashing"; // Unused for now as we hardcode phash

    while ((opt = getopt_long(argc, argv, "m:dhv", long_options, NULL)) != -1) {
        switch (opt) {
            case 'm':
                // method = optarg;
                // TODO: Support other methods
                if (strcmp(optarg, "PerceptualHashing") != 0) {
                    fprintf(stderr, "Warning: Only PerceptualHashing is currently supported.\n");
                }
                break;
            case 'd':
                decompress = 1;
                break;
            case 'h':
                print_usage(argv[0]);
                return 0;
            case 'v':
                printf("vhcalc %s\n", VHCALC_VERSION);
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }

    const char *input_path = "-";

    if (optind < argc) {
        input_path = argv[optind];
    }

    FILE *in_stream = NULL;
    video_reader_t *video_ctx = NULL;
    int use_stdio = 0;

    if (decompress) {
        if (strcmp(input_path, "-") == 0) {
            in_stream = stdin;
        } else {
            in_stream = fopen(input_path, "rb");
            if (!in_stream) {
                perror("fopen");
                return 1;
            }
        }

        // Read 8 bytes chunks, print as hex
        uint8_t buf[8];
        while (fread(buf, 1, 8, in_stream) == 8) {
            uint64_t h = bytes_to_uint64(buf);
            print_hash_hex(h, stdout);
        }

        if (in_stream != stdin) {
            fclose(in_stream);
        }
    } else {
        // Hashing mode: Use video reader (ffmpeg)
        // If input_path is "-", ffmpeg will read from stdin
        video_ctx = video_reader_open(input_path);
        if (!video_ctx) {
            fprintf(stderr, "Failed to open video file or spawn ffmpeg.\n");
            return 1;
        }

        // Read 32x32 frames, compute hash, write binary
        uint8_t frame[32 * 32];
        size_t n;
        while (1) {
            n = video_reader_read(video_ctx, frame, 32 * 32);

            if (n != 32 * 32) break;

            uint64_t h = phash_compute(frame);
            write_hash_binary(h, stdout);
        }
    }

    if (video_ctx) {
        video_reader_close(video_ctx);
    }
    if (use_stdio && in_stream != stdin) {
        fclose(in_stream);
    }

    return 0;
}
