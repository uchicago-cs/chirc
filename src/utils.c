/* See utils.h for details about the functions in this module */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "utils.h"

/* Add your helper functions here.
 *
 * Careful: This module is intended for functions that may be needed in multiple
 *          modules. If a helper function is only used in a single C file, then it
 *          probably belongs there, not in this module. */

/* See utils.h */
void *xmalloc(size_t size)
{
    void *p = malloc(size);
    if (!p) {
        fprintf(stderr, "Out of memory\n");
        abort();
    }
    return p;
}


/* See utils.h */
void *xcalloc(size_t nmemb, size_t size)
{
    void *p = calloc(nmemb, size);
    if (!p) {
        fprintf(stderr, "Out of memory\n");
        abort();
    }
    return p;
}


/* See utils.h */
bool has_mode(const char *modes, char mode)
{
    return strchr(modes, mode) != NULL;
}


/* See utils.h */
int set_mode(char *modes, size_t size, char mode)
{
    size_t len;

    if (has_mode(modes, mode))
        return 1;

    /* Make sure there is room for the mode and the terminating '\0' */
    len = strlen(modes);
    if (len + 1 >= size)
        return 1;

    modes[len] = mode;
    modes[len + 1] = '\0';

    return 0;
}


/* See utils.h */
int remove_mode(char *modes, char mode)
{
    char *p;

    p = strchr(modes, mode);
    if(!p)
        return 1;
    else
        while(*p)
        {
            *p = *(p + 1);
            p++;
        }

    return 0;
}
