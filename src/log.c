/* See log.h for details about the functions in this module */

#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <time.h>

#include "log.h"


/* Logging level. Set by default to print just informational messages */
static loglevel_t loglevel = INFO;


void chirc_setloglevel(loglevel_t level)
{
    loglevel = level;
}

/* This function does the actual logging and is called by chilog()
 * and serverlog(). It has a va_list parameter instead of being a
 * variadic function. The prefix is printed verbatim before the
 * formatted message (it is never interpreted as a format string) */
CHIRC_PRINTF_FORMAT(3, 0)
static void vchilog(loglevel_t level, const char *prefix, const char *fmt, va_list argptr)
{
    time_t t;
    char buf[80];
    const char *levelstr;

    if(level > loglevel)
        return;

    t = time(NULL);
    struct tm tt;
    localtime_r(&t, &tt);
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &tt);

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
    printf("[%s] %6s %s", buf, levelstr, prefix);

    vprintf(fmt, argptr);
    printf("\n");
    funlockfile(stdout);
    fflush(stdout);
}

/* See log.h */
void chilog(loglevel_t level, const char *fmt, ...)
{
    va_list argptr;

    va_start(argptr, fmt);
    vchilog(level, "", fmt, argptr);
    va_end(argptr);
}

/* See log.h */
void serverlog(loglevel_t level, chirc_connection_t *conn, const char *fmt, ...)
{
    char buf[256];

    buf[0] = '\0';
    if (conn)
    {
        if(conn->type == CONN_TYPE_UNKNOWN)
        {
            snprintf(buf, sizeof(buf), "%s -- ", conn->hostname);
        }
        else if(conn->type == CONN_TYPE_USER)
        {
            chirc_user_t *user = conn->peer.user;
            if(user->nick)
                snprintf(buf, sizeof(buf), "%s!%s@%s -- ", user->nick, user->username, conn->hostname);
            else
                snprintf(buf, sizeof(buf), "unknown!unknown@%s -- ", conn->hostname);
        }
        else if (conn->type == CONN_TYPE_SERVER)
        {
            snprintf(buf, sizeof(buf), "%s -- ", conn->peer.server->servername);
        }
    }

    va_list argptr;

    va_start(argptr, fmt);
    vchilog(level, buf, fmt, argptr);
    va_end(argptr);
}
