#define _POSIX_C_SOURCE 200809L
#include "video_reader.h"
#include "config.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>

struct video_reader {
    int fd;
    pid_t pid;
};

video_reader_t *video_reader_open(const char *filename) {
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        perror("pipe");
        return NULL;
    }

    pid_t pid = fork();
    if (pid == -1) {
        perror("fork");
        close(pipefd[0]);
        close(pipefd[1]);
        return NULL;
    }

    if (pid == 0) {
        // Child
        close(pipefd[0]); // Close read end
        if (dup2(pipefd[1], STDOUT_FILENO) == -1) {
            perror("dup2");
            exit(1);
        }
        close(pipefd[1]);

        // Construct arguments
        // ffmpeg -v quiet -hide_banner -nostdin -i filename -vf scale=32:32,format=gray -f rawvideo -
        char scale_filter[64];
        snprintf(scale_filter, sizeof(scale_filter), "scale=%d:%d,format=gray", DEFAULT_FRAME_WIDTH, DEFAULT_FRAME_HEIGHT);

        char *const args[] = {
            "ffmpeg",
            "-v", "quiet",
            "-hide_banner",
            "-nostdin",
            "-i", (char *)filename,
            "-vf", scale_filter,
            "-f", "rawvideo",
            "-",
            NULL
        };

        execvp("ffmpeg", args);
        perror("execvp");
        exit(1);
    }

    // Parent
    close(pipefd[1]); // Close write end

    video_reader_t *ctx = malloc(sizeof(video_reader_t));
    if (!ctx) {
        close(pipefd[0]);
        kill(pid, SIGTERM);
        waitpid(pid, NULL, 0);
        return NULL;
    }

    ctx->fd = pipefd[0];
    ctx->pid = pid;
    return ctx;
}

size_t video_reader_read(video_reader_t *ctx, void *buf, size_t count) {
    if (!ctx) return 0;

    size_t total_read = 0;
    while (total_read < count) {
        ssize_t n = read(ctx->fd, (char*)buf + total_read, count - total_read);
        if (n > 0) {
            total_read += n;
        } else if (n == 0) {
            // EOF
            break;
        } else {
            if (errno == EINTR) continue;
            return total_read; // Error
        }
    }
    return total_read;
}

void video_reader_close(video_reader_t *ctx) {
    if (ctx) {
        close(ctx->fd);
        // Wait for child
        int status;
        waitpid(ctx->pid, &status, 0);
        free(ctx);
    }
}
