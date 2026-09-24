#include <stdio.h>
#include <stdlib.h>

/* Read an entire file into a newly allocated, NUL-terminated buffer.
 * Returns NULL on failure; the caller must free() the result. */
char *read_file(const char *path, size_t *len_out) {
    FILE *fp = fopen(path, "rb");
    if (!fp) return NULL;

    fseek(fp, 0, SEEK_END);
    long len = ftell(fp);
    rewind(fp);

    char *buf = malloc((size_t)len + 1);
    if (!buf) {
        fclose(fp);
        return NULL;
    }
    size_t n = fread(buf, 1, (size_t)len, fp);
    buf[n] = '\0';
    fclose(fp);

    if (len_out) *len_out = n;
    return buf;
}
