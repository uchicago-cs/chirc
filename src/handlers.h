/*! \file handlers.h
 *  \brief Message handlers
 *
 *  This module implements a dispatch table that provides a uniform
 *  interface for implementing the handling of each IRC command.
 *
 *  The only function that should be called from the rest of the call
 *  is chirc_handle which, based on the message to process, will dispatch
 *  it to the appropriate handler function.
 *
 *  See handler.c for details on how the dispatch table is implemented
 *  (and how to implement new commands)
 */

#ifndef HANDLERS_H_
#define HANDLERS_H_

#include "ctx.h"
#include "connection.h"
#include "message.h"

/*! Return code that indicates that the outcome of processing
 *  the message is that the server must close the connection
 *  (e.g., when receiving a QUIT message) */
#define CHIRC_HANDLER_DISCONNECT	(-42)

/*! \brief Process (handle) a message received by the server
 *
 * \param ctx Server context
 * \param conn Connection the message arrived through
 * \param msg The message to process
 * \return If the message was handled correctly, returns 0 (CHIRC_OK).
 *         In some commands, the expected outcome of the command is
 *         for the connection to be closed (e.g., the QUIT command)
 *         In those cases, chirc_handle will return -42 (CHIRC_HANDLER_DISCONNECT).
 *         If the handling of the message fails,  a non-zero value
 *         (other than -42) will be returned.
 */
int chirc_handle(chirc_ctx_t *ctx, chirc_connection_t *conn, chirc_message_t *msg);

#endif /* HANDLERS_H_ */
