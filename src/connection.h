/*! \file connection.h
 *  \brief Functions related to chirc_connection_t
 *
 *  This module provides functions related to the chirc_connection_t struct
 *  (defined in chirc.h).
 *
 *  An instance of a chirc_connection_t struct represents an *inbound* connection
 *  into the server (i.e., a peer that has connected to the server).
 *
 *  The peer of the connection can be either an IRC user, or another IRC server
 *  (if we are running an IRC network)
 */
#ifndef CONNECTION_H_
#define CONNECTION_H_

#include "chirc.h"

/*! \brief Initializes a chirc_connection_t struct
 *
 * This function assumes that memory has already been allocated
 * for the struct, and will initialize its fields.
 *
 * \param conn The connection to initialize
 */
void chirc_connection_init(chirc_connection_t *conn);


/*! \brief Frees a chirc_connection_t struct
 *
 * This function frees memory allocated to the fields of a
 * chirc_connection_t struct, but does not free the struct
 * itself (doing so is the responsibility of the caller
 * of this function)
 *
 * \param conn The connection to free
 */
void chirc_connection_free(chirc_connection_t *conn);

/*! \brief Send a message through a connection
 *
 * \param ctx Server context
 * \param conn The connection to send the message through
 * \param msg The message to send
 * \return 0 on success, non-zero on failure
 */
int chirc_connection_send_message(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg);

/*! \brief Creates a thread to handle a connection
 *
 * \param ctx Server context
 * \param conn The connection that will be handled by the thread
 * \return 0 on success, non-zero on failure
 */
int create_connection_thread(chirc_ctx_t *ctx, chirc_connection_t *conn);

#ifndef CHIRC_HIDE_CODE
int chirc_connection_disconnect(chirc_ctx_t *ctx, chirc_connection_t *conn, char *quitmsg);
bool chirc_connection_is_registered(chirc_connection_t *conn);
#endif

#endif /* USER_H_ */
