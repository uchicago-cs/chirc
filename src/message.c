/* See message.h for details about the functions in this module */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
#include "message.h"
#include "reply.h"
#include "connection.h"
#include "utils.h"

/* See message.h */
int chirc_message_from_string(chirc_message_t *msg, const char *s)
{
    char *p, *trailing, *token, *saveptr;
    sds raw;

    /* Initialize all chirc_message_t fields to zero */
    *msg = (chirc_message_t) {0};

    /* We make a copy of the message (without the trailing "\r\n"). The
     * prefix, command, and parameters will all point into this copy. */
    raw = sdstrim(sdsnew(s), "\r\n");

    /* Skip over any leading spaces */
    p = raw + strspn(raw, " ");

    /* The long parameter (if any) starts at the first " :" and includes
     * the rest of the message, so we split it off before tokenizing */
    trailing = strstr(p, " :");
    if (trailing)
    {
        *trailing = '\0';
        trailing += 2;
    }

    token = strtok_r(p, " ", &saveptr);
    if (token && token[0] == ':')
    {
        msg->prefix = token + 1;
        /* If the message starts with a prefix, there
           has to be something after the prefix */
        token = strtok_r(NULL, " ", &saveptr);
    }

    /* If there was no token (because the message is empty or because
     * there was nothing after the prefix), this is not a valid message */
    if (!token)
    {
        sdsfree(raw);
        return -1;
    }

    /* Make the command all uppercase */
    msg->cmd = token;
    for(char *c = token; *c; c++)
        *c = toupper((unsigned char) *c);

    /* Extract the remaining parameters, except the long parameter */
    while (msg->nparams < MSG_MAX_PARAMS && (token = strtok_r(NULL, " ", &saveptr)))
        msg->params[msg->nparams++] = token;

    /* If there is a long parameter, save it (as long as we haven't
     * reached the maximum number of parameters) */
    if (trailing && msg->nparams < MSG_MAX_PARAMS)
    {
        msg->params[msg->nparams++] = trailing;
        msg->longlast = true;
    }

    msg->raw = raw;

    return 0;
}


/* See message.h */
int chirc_message_to_string(chirc_message_t *msg, char **s)
{
    /* We build the string with sds, so it can grow as needed (messages
     * longer than MSG_MAX are truncated when they are sent) */
    sds str = sdsempty();

    if (msg->prefix)
        str = sdscatprintf(str, ":%s ", msg->prefix);

    str = sdscat(str, msg->cmd);

    for(unsigned int i=0; i < msg->nparams; i++)
    {
        bool long_param = (i == msg->nparams - 1 && msg->longlast);
        str = sdscat(str, long_param ? " :" : " ");
        str = sdscat(str, msg->params[i]);
    }

    str = sdscat(str, "\r\n");

    /* Return a regular C string, to avoid breaking existing code.
     * At a later point, we will make this module use SDS strings
     * exclusively. */
    *s = strdup(str);
    sdsfree(str);

    return 0;
}


/* See message.h */
int chirc_message_construct(chirc_message_t *msg, const char *prefix, const char *cmd)
{
    if (prefix)
        msg->prefix = strdup(prefix);
    else
        msg->prefix = NULL;

    msg->cmd = strdup(cmd);
    msg->nparams = 0;
    msg->longlast = false;
    msg->raw = NULL;

    return 0;
}


/* See message.h */
int chirc_message_add_parameter(chirc_message_t *msg, const char *param, bool longlast)
{
    if (msg->nparams >= MSG_MAX_PARAMS)
        return CHIRC_FAIL;

    msg->params[msg->nparams++] = strdup(param);
    msg->longlast = longlast;

    return 0;
}


/* See message.h */
int chirc_message_construct_reply(chirc_message_t *msg, chirc_ctx_t *ctx, chirc_connection_t *conn, const char *code)
{
    assert(strlen(code) == 3);

    chirc_message_construct(msg, ctx->network.this_server->servername, code);

    if (conn->type == CONN_TYPE_UNKNOWN)
    {
        chirc_message_add_parameter(msg, "*", false);
    }
    else if (conn->type == CONN_TYPE_USER)
    {
        chirc_user_t *user = conn->peer.user;

        if (!user->nick)
            chirc_message_add_parameter(msg, "*", false);
        else
            chirc_message_add_parameter(msg, user->nick, false);
    }
    else if (conn->type == CONN_TYPE_SERVER)
    {
        chirc_server_t *server = conn->peer.server;

        if (!server->servername)
            chirc_message_add_parameter(msg, "*", false);
        else
            chirc_message_add_parameter(msg, server->servername, false);
    }

    return 0;
}


/* See message.h */
void chirc_message_free(chirc_message_t *msg)
{
    if(msg->raw)
    {
        /* The prefix, command, and parameters point into the raw string */
        sdsfree(msg->raw);
    }
    else
    {
        free(msg->prefix);
        free(msg->cmd);
        for(unsigned int i=0; i < msg->nparams; i++)
        {
            free(msg->params[i]);
        }
    }
}

