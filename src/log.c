/*
 *  chirc
 *
 *  Logging functions
 *
 *  see log.h for descriptions of functions, parameters, and return values.
 *
 */

#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <time.h>

#include "log.h"

/* Logging level. Set by default to print just informational messages */
static int loglevel = INFO;


void chirc_setloglevel(loglevel_t level)
{
    loglevel = level;
}

/* This function does the actual logging and is called by chilog().
 * It has a va_list parameter instead of being a variadic function */
void __chilog(loglevel_t level, char *fmt, va_list argptr)
{
    time_t t;
    char buf[80], *levelstr;

    if(level > loglevel)
        return;

    t = time(NULL);
    strftime(buf,80,"%Y-%m-%d %H:%M:%S",localtime(&t));

    switch(level)
    {
    case CRITICAL:
        levelstr = "CRITIC";
        break;
    case ERROR:
        levelstr = "ERROR";
        break;
    case WARNING:
        levelstr = "WARN";
        break;
    case INFO:
        levelstr = "INFO";
        break;
    case DEBUG:
        levelstr = "DEBUG";
        break;
    case TRACE:
        levelstr = "TRACE";
        break;
    default:
        levelstr = "UNKNOWN";
        break;
    }

    flockfile(stdout);
    printf("[%s] %6s ", buf, levelstr);

    vprintf(fmt, argptr);
    printf("\n");
    funlockfile(stdout);
    fflush(stdout);
}

void chilog(loglevel_t level, char *fmt, ...)
{
    va_list argptr;

    va_start(argptr, fmt);
    __chilog(level, fmt, argptr);
    va_end(argptr);
}

