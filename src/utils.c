/* See utils.h for details about the functions in this module */

#include <string.h>

/* Add your helper functions here.
 *
 * Careful: This module is intended for functions that may be needed in multiple
 *          modules. If a helper function is only used in a single C file, then it
 *          probably belongs there, not in this module. */

/* See utils.h */
int has_mode(char *modes, char mode)
{
    if (strchr(modes, mode))
        return 1;
    else
        return 0;
}


/* See utils.h */
int set_mode(char *modes, char mode)
{
    char modestr[2] = { mode, '\0' };

    if (has_mode(modes, mode))
        return 1;
    else
    {
        strcat(modes,modestr);
        return 0;
    }
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
