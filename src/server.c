/* See server.h for details about the functions in this module */

#include <string.h>
#include "server.h"

/* See server.h */
void chirc_server_init(chirc_server_t *server)
{
    server->servername = NULL;
    server->hostname = NULL;
    server->port = NULL;
    server->passwd = NULL;
    server->registered = false;

    server->conn = NULL;
}

/* See server.h */
void chirc_server_free(chirc_server_t *server)
{
    sdsfree(server->servername);
    sdsfree(server->hostname);
    sdsfree(server->port);
    sdsfree(server->passwd);
}
