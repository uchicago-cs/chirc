/* See message.h for details about the functions in this module */

#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
#include "message.h"
#include "reply.h"
#include "connection.h"

/* See message.h */
int chirc_message_from_string(chirc_message_t *msg, char *s)
{
    char *params[15], *pch, *msgstr, *i, *saveptr;
    unsigned int len;

    len = strlen(s);

    msg->nparams = 0;

    msgstr = malloc(len);

    strncpy(msgstr, s, len - 2);
    msgstr[len-2] = '\0';

    // For ":" lookahead
    msgstr[len-1] = '\0';

    pch = strtok_r(msgstr, " ", &saveptr);
    if (!pch)
    {
        free(msgstr);
        return -1;
    }

    if (*pch == ':')
    {
        msg->prefix = pch+1;
        pch = strtok_r(NULL, " ", &saveptr);
        /* If the message starts with a prefix, there
           has to be something after the prefix */
        if (!pch)
        {
            free(msgstr);
            return -1;
        }
    }
    else
        msg->prefix = NULL;

    msg->cmd = pch;
    for(i=pch; *i; i++)
        *i = toupper(*i);

    msg->longlast = 0;

    while (pch != NULL)
    {
        i = pch;
        while (*i++) ;

        if (*i == ':')
        {
            params[msg->nparams++] = i + 1;
            msg->longlast = 1;
            break;
        }

        pch = strtok_r(NULL, " ", &saveptr);
        if(!pch)
            break;
        params[msg->nparams++] = pch;
    }

    for (int i=0; i < msg->nparams; i++)
    {
        msg->params[i] = params[i];
    }

    msg->raw = msgstr;

    return 0;
}


/* See message.h */
int chirc_message_to_string(chirc_message_t *msg, char **s)
{
    char buffer[1024];

    buffer[0] = '\0';

    if (msg->prefix)
    {
        strcat(buffer, ":");
        strcat(buffer, msg->prefix);
        strcat(buffer, " ");
    }

    strcat(buffer, msg->cmd);

    for(int i=0; i < msg->nparams; i++)
    {
        strcat(buffer, " ");
        if (i== msg->nparams - 1 && msg->longlast)
            strcat(buffer, ":");
        strcat(buffer, msg->params[i]);
    }
    strcat(buffer,"\r\n");

    *s = strdup(buffer);

    return 0;
}


/* See message.h */
int chirc_message_construct(chirc_message_t *msg, char *prefix, char *cmd)
{
    if (prefix)
        msg->prefix = strdup(prefix);
    else
        msg->prefix = NULL;

    msg->cmd = strdup(cmd);
    msg->nparams = 0;
    msg->longlast = 0;
    msg->raw = NULL;

    return 0;
}


/* See message.h */
int chirc_message_add_parameter(chirc_message_t *msg, char *param, bool longlast)
{
    msg->params[msg->nparams++] = strdup(param);
    msg->longlast = longlast;

    return 0;
}


/* See message.h */
int chirc_message_construct_reply(chirc_message_t *msg, chirc_ctx_t *ctx, chirc_connection_t *conn, char *code)
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
        free(msg->raw);
    }
    else
    {
        free(msg->prefix);
        free(msg->cmd);
        for(int i=0; i < msg->nparams; i++)
        {
            free(msg->params[i]);
        }
    }
}

