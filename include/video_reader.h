#ifndef VIDEO_READER_H
#define VIDEO_READER_H

#include <stddef.h>
#include <stdint.h>

typedef struct video_reader video_reader_t;

/**
 * Opens a video file using ffmpeg.
 *
 * @param filename Path to video file.
 * @return Pointer to video reader context, or NULL on error.
 */
video_reader_t *video_reader_open(const char *filename);

/**
 * Reads raw bytes from the video stream.
 *
 * @param ctx Reader context.
 * @param buf Buffer to read into.
 * @param count Number of bytes to read.
 * @return Number of bytes read.
 */
size_t video_reader_read(video_reader_t *ctx, void *buf, size_t count);

/**
 * Closes the video reader and waits for the subprocess.
 *
 * @param ctx Reader context.
 */
void video_reader_close(video_reader_t *ctx);

#endif // VIDEO_READER_H
