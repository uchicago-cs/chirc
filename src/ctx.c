/* See ctx.h for details about the functions in this module */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sds.h>

#include "ctx.h"
#include "user.h"
#include "channel.h"
#include "channeluser.h"
#include "server.h"
#include "log.h"
#include "chirc.h"

/* See ctx.h */
void chirc_ctx_init(chirc_ctx_t *ctx)
{
    time_t t = time(NULL);

    ctx->channels = NULL;

    ctx->users = NULL;

    ctx->connections = NULL;

    ctx->network.this_server = NULL;
    ctx->network.servers = NULL;

    ctx->version = sdsnew(VERSION);
    localtime_r(&t, &ctx->created);
}

/* See ctx.h */
void chirc_ctx_free(chirc_ctx_t *ctx)
{
    sdsfree(ctx->version);

    /* Free channels */
    chirc_channel_t *channel;
    for(channel = ctx->channels; channel != NULL; channel = channel->hh.next)
    {
        /* Note: Once we publish the code for the channels module, we will
         * update this function to call the chirc_channel_free function */
    }
    HASH_CLEAR(hh, ctx->channels);

    /* Free users */
    chirc_user_t *user;
    for(user = ctx->users; user != NULL; user = user->hh.next)
    {
        chirc_user_free(user);
    }
    HASH_CLEAR(hh, ctx->users);

    /* Free connections */
    chirc_connection_t *conn;
    for(conn = ctx->connections; conn != NULL; conn = conn->hh.next)
    {
        chirc_connection_free(conn);
    }
    HASH_CLEAR(hh, ctx->connections);

    /* Free servers */
    if (ctx->network.servers)
    {
        /* If we're running in network mode, we need to free the servers
         * in the servers hash table */
        chirc_server_t *server;
        for(server = ctx->network.servers; server != NULL; server = server->hh.next)
        {
            chirc_server_free(server);
        }
        HASH_CLEAR(hh, ctx->connections);
    }
    else
    {
        /* If we're running in standalone mode, we only need to free
         * the network.this_server struct */
        chirc_server_free(ctx->network.this_server);
        free(ctx->network.this_server);
    }

}


/* See ctx.h */
void chirc_ctx_add_connection(chirc_ctx_t *ctx, chirc_connection_t *conn)
{
    HASH_ADD_INT(ctx->connections, socket, conn);
}


/* See ctx.h */
void chirc_ctx_remove_connection(chirc_ctx_t *ctx, chirc_connection_t *conn)
{
    HASH_DEL(ctx->connections, conn);
}


/* See ctx.h */
int chirc_ctx_numusers(chirc_ctx_t *ctx)
{
    int n = 0;
    for (chirc_user_t *u = ctx->users; u != NULL; u = u->hh.next)
    {
        if (u->registered)
            n++;
    }

    return n;
}


/* See ctx.h */
int chirc_ctx_numchannels(chirc_ctx_t *ctx)
{
    int size;

    size = HASH_COUNT(ctx->channels);

    return size;
}


/* See ctx.h */
int chirc_ctx_numops(chirc_ctx_t *ctx)
{
    int n = 0;

    for (chirc_user_t *u = ctx->users; u != NULL; u = u->hh.next)
    {
        if (chirc_user_has_mode(u, 'o'))
            n++;
    }

    return n;
}


/* See ctx.h */
int chirc_ctx_unknown_connections(chirc_ctx_t *ctx)
{
    int n=0;

    for (chirc_connection_t *c = ctx->connections; c != NULL; c = c->hh.next)
    {
        if (c->type == CONN_TYPE_UNKNOWN)
            n++;
    }

    return n;
}


/* See ctx.h */
chirc_channel_t* chirc_ctx_get_channel(chirc_ctx_t *ctx, char *channelname)
{
    chirc_channel_t *channel;

    HASH_FIND_STR(ctx->channels, channelname, channel);

    return channel;
}


/* See ctx.h */
int chirc_ctx_add_channel(chirc_ctx_t *ctx, chirc_channel_t *channel)
{
    HASH_ADD_KEYPTR(hh, ctx->channels, channel->name, sdslen(channel->name), channel);

    return CHIRC_OK;
}


/* See ctx.h */
bool chirc_ctx_get_or_create_channel(chirc_ctx_t *ctx, char *channelname, chirc_channel_t **channel)
{
    bool created;


    HASH_FIND_STR(ctx->channels, channelname, *channel);
    if(*channel)
    {
        created = false;
    }
    else
    {
        created = true;

        *channel = malloc(sizeof(chirc_channel_t));
        chirc_channel_init(*channel);
        (*channel)->name = sdsnew(channelname);
        HASH_ADD_KEYPTR(hh, ctx->channels, (*channel)->name, sdslen((*channel)->name), *channel);
    }

    return created;
}


/* See ctx.h */
int chirc_ctx_remove_channel(chirc_ctx_t *ctx, chirc_channel_t *channel)
{
    HASH_DEL(ctx->channels, channel);

    return CHIRC_OK;
}


/* See ctx.h */
chirc_user_t* chirc_ctx_get_user(chirc_ctx_t *ctx, char *nick)
{
    chirc_user_t *user;

    HASH_FIND_STR(ctx->users, nick, user);

    return user;
}


/* See ctx.h */
int chirc_ctx_add_user(chirc_ctx_t *ctx, chirc_user_t *user)
{
    HASH_ADD_KEYPTR(hh, ctx->users, user->nick, sdslen(user->nick), user);

    return CHIRC_OK;
}

/* See ctx.h */
bool chirc_ctx_get_or_create_user(chirc_ctx_t *ctx, char *nick, chirc_user_t **user)
{
    bool created;


    HASH_FIND_STR(ctx->users, nick, *user);
    if(*user)
    {
        created = false;
    }
    else
    {
        created = true;

        *user = malloc(sizeof(chirc_user_t));
        chirc_user_init(*user);
        (*user)->nick = sdsnew(nick);
        HASH_ADD_KEYPTR(hh, ctx->users, (*user)->nick, sdslen((*user)->nick), *user);
    }

    return created;
}


int chirc_ctx_remove_user(chirc_ctx_t *ctx, chirc_user_t *user)
{
    HASH_DEL(ctx->users, user);

    return CHIRC_OK;
}



/* See ctx.h */
chirc_server_t* chirc_ctx_get_server(chirc_ctx_t *ctx, char *servername)
{
    chirc_server_t *server;

    HASH_FIND_STR(ctx->network.servers, servername, server);

    return server;
}


/* See ctx.h */
int chirc_ctx_add_server(chirc_ctx_t *ctx, chirc_server_t *server)
{
    HASH_ADD_KEYPTR(hh, ctx->network.servers, server->servername, sdslen(server->servername), server);

    return CHIRC_OK;
}


/* See ctx.h */
int chirc_ctx_load_network(chirc_ctx_t *ctx, char *file, char *servername)
{
    FILE *fp;
    char *l = NULL;
    size_t len = 0;
    ssize_t read;

    fp = fopen(file, "r");
    if (fp == NULL)
    {
        serverlog(CRITICAL, NULL, "Could not read file %s\n", file);
        return CHIRC_FAIL;
    }

    while ((read = getline(&l, &len, fp)) != -1)
    {
        sds line = sdsnew(l);
        line = sdstrim(line, " \r\n");
        sds *tokens;
        int count;

        tokens = sdssplitlen(line, sdslen(line),",",1, &count);

        if (count != 4)
        {
            serverlog(CRITICAL, NULL, "Invalid line in network file: %s", line);
            return CHIRC_FAIL;
        }

        chirc_server_t *ns;

        ns = chirc_ctx_get_server(ctx, tokens[0]);

        if (ns)
        {
            serverlog(CRITICAL, NULL, "Network file contains duplicate server name: %s", ns->servername);
            return CHIRC_FAIL;
        }

        ns = calloc(1, sizeof(chirc_server_t));

        ns->servername = tokens[0];
        ns->hostname = tokens[1];
        ns->port = tokens[2];
        ns->passwd = tokens[3];
        ns->conn = NULL;

        chirc_ctx_add_server(ctx, ns);

        if (strcmp(ns->servername, servername) == 0)
        {
            ctx->network.this_server = ns;
        }
    }

    fclose(fp);
    free(l);

    if (ctx->network.this_server == NULL)
    {
        serverlog(CRITICAL, NULL, "Network file does not include an entry for %s", servername);
        return CHIRC_FAIL;
    }

    return CHIRC_OK;
}
