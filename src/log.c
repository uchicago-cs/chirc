/* See log.h for details about the functions in this module */

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

/* See log.h */
void chilog(loglevel_t level, char *fmt, ...)
{
    va_list argptr;

    va_start(argptr, fmt);
    __chilog(level, fmt, argptr);
    va_end(argptr);
}

/* See log.h */
void serverlog(loglevel_t level, chirc_connection_t *conn, char *fmt, ...)
{
    char buf[256];

    if (conn)
    {
        if(conn->type == CONN_TYPE_UNKNOWN)
        {
            sprintf(buf, "%s -- ", conn->hostname);
        }
        else if(conn->type == CONN_TYPE_USER)
        {
            chirc_user_t *user = conn->peer.user;
            if(user->nick)
                sprintf(buf, "%s!%s@%s -- ", user->nick, user->username, conn->hostname);
            else
                sprintf(buf, "unknown!unknown@%s -- ", conn->hostname);
        }
        else if (conn->type == CONN_TYPE_SERVER)
        {
            sprintf(buf, "%s -- ", conn->peer.server->servername);
        }
    }
    else
        buf[0] = '\0';

    strncat(buf, fmt, 256 - strlen(buf) - 1);

    va_list argptr;

    va_start(argptr, fmt);
    __chilog(level, buf, argptr);
    va_end(argptr);
}
