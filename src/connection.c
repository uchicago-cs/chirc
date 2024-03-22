/* See connection.h for details about the functions in this module */

#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <pthread.h>
#include <sys/socket.h>

#include "ctx.h"
#include "connection.h"
#include "utils.h"
#include "message.h"
#include "handlers.h"
#include "chirc.h"
#include "log.h"

/* See connection.h */
void chirc_connection_init(chirc_connection_t *conn)
{
    conn->type = CONN_TYPE_UNKNOWN;

    conn->hostname = NULL;
    conn->port = 0;

}


/* See connection.h */
void chirc_connection_free(chirc_connection_t *conn)
{
    sdsfree(conn->hostname);

}


/* See connection.h */
int chirc_connection_send_message(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg)
{
    /* Your code here */
    return CHIRC_OK;
}


/* See connection.h */
int create_connection_thread(chirc_ctx_t *ctx, chirc_connection_t *connection)
{
    /* Your code here */

    return CHIRC_OK;
}

