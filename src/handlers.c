/*
 * Message handlers
 *
 * In chirc, the code to process each IRC command is contained in
 * a function that looks like this:
 *
 *     int chirc_handle_COMMAND(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg);
 *
 * e.g., the handler function for PRIVMSG would be chirc_handle_PRIVMSG
 * (with the same parameters shown above)
 *
 * These functions are added to a dispatch table that allows us
 * to easily dispatch messages to the correct function based
 * on their command.
 *
 * A dispatch table is basically a table that maps a key (in this
 * case, an IRC command) to a function pointer. So, given
 * a command name, we can find the function that will handle
 * that command. In our code, this table is implemented
 * via the "handlers" array contained in this module.
 *
 * To implement a new command, you will need to implement a
 * handler function for that command, and update the "handlers"
 * array to add an entry for the new command. See the code
 * below for more details.
 *
 */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <assert.h>
#include <sys/socket.h>
#include <netdb.h>
#include "ctx.h"
#include "channel.h"
#include "channeluser.h"
#include "handlers.h"
#include "reply.h"
#include "log.h"
#include "connection.h"
#include "chirc.h"
#include "message.h"
#include "user.h"
#include "server.h"


/* The following typedef defines a type called "handler_function"
 * for the function pointers in the handlers array. */
typedef int (*handler_function_t)(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg);


/* Forward declaration of handler functions */

// Miscellaneous messages
int chirc_handle_PING(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg);
int chirc_handle_PONG(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg);



/*! \struct handler_entry
 * \brief Entry in the handler dispatch table
 *
 * This struct represents one entry in the dispatch table:
 * a command name and a function pointer to a handler function
 * (using the handler_function_t type we defined earlier) */
struct handler_entry
{
    char *name;
    handler_function_t func;
};

/* Convenience macro for specifying entries in the dispatch table */
#define HANDLER_ENTRY(NAME) { #NAME, chirc_handle_ ## NAME}

/* Null entry in the dispatch table. This must always be the last
 * entry in the dispatch table */
#define NULL_ENTRY			{ NULL, NULL }


/* The dispatch table (an array of handler_entry structs).
 * To add a new entry (e.g., for command FOOBAR) add a new
 * line that looks like this:
 *
 *     HANDLER_ENTRY (FOOBAR)
 *
 * Make sure to add it *before* the NULL_ENTRY entry, which
 * must always come last.
 */
struct handler_entry handlers[] =
{
    HANDLER_ENTRY (PING),
    HANDLER_ENTRY (PONG),

    NULL_ENTRY
};


/* See handlers.h */
int chirc_handle(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg)
{
    chirc_message_t reply;
    int rc=0, h;

    /* Print message to the server log */
    serverlog(DEBUG, conn, "Handling command %s", msg->cmd);
    for(int i=0; i<msg->nparams; i++)
        serverlog(DEBUG, conn, "%s[%i] = %s", msg->cmd, i + 1, msg->params[i]);

    /* Search the dispatch table for an entry corresponding to the
     * message we are processing */
    for(h=0; handlers[h].name != NULL; h++)
        if (!strcmp(msg->cmd, handlers[h].name))
        {

            rc = handlers[h].func(ctx, conn, msg);
            break;
        }


    return rc;
}


int chirc_handle_PING(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg)
{
    /* Construct a reply to the PING */
    chirc_message_t reply;
    chirc_message_construct(&reply, NULL, "PONG");
    chirc_message_add_parameter(&reply, ctx->network.this_server->servername, 0);

    /* Send the message */
    if(chirc_connection_send_message(ctx, conn, &reply))
    {
        chirc_message_free(&reply);
        return CHIRC_HANDLER_DISCONNECT;
    }

    /* Free the reply */
    chirc_message_free(&reply);

    return CHIRC_OK;
}

int chirc_handle_PONG(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg)
{
    /* PONG messages are ignored, so we don't do anything */

    return CHIRC_OK;
}


