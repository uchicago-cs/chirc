/*! \file message.h
 *  \brief Functions related to chirc_message_t
 *
 *  The chirc_message_t struct (defined in chirc.h), and the functions
 *  in this module, provide a convenient mechanism to parse IRC message,
 *  as well as to create new messages.
 *
 *  To parse a string containing an IRC message, use the chirc_message_from_string
 *  function. For example:
 *
 *      chirc_message_t *msg = malloc(sizeof(chirc_message_t));
 *      chirc_message_from_string(msg, "PRIVMSG jrandom :Hello, how are you?");
 *
 *  chirc_message_from_string will initialize all the fields in the msg variable
 *  to reflect the contents of the message string. For example:
 *
 *      msg->cmd        <-- This will contain "PRIVMSG"
 *      msg->params[0]  <-- THis will contain "jrandom"
 *      msg->params[1]  <-- This will contain "Hello, how are you?"
 *      msg->nparams    <-- THis will contain 2
 *
 *  Note that you should not edit the fields of a chirc_message_t yourself.
 *
 *  To create a new message from scratch, you can use the chirc_message_construct
 *  function. For example:
 *
        chirc_message_t *msg = malloc(sizeof(chirc_message_t));
 *      chirc_message_construct(msg, NULL, "PRIVMSG");
 *
 *  This will construct a PRIVMSG message with no prefix and with no parameters
 *  (so far). To add parameters to the message, use the chirc_message_add_parameter
 *  function. For example:
 *
 *      chirc_message_add_parameter(msg, "jrandom", false);
 *      chirc_message_add_parameter(msg, "Hello, how are you?", true);
 *
 *  The third parameter (longlast) indicates whether the parameter is a "long parameter"
 *  (i.e., whether it should be rendered with a ":" before it).
 *
 *  This module also provides a chirc_reply_numeric_construct function that can be used
 *  to construct messages that are specifically replies.
 *
 *  Once a message has been constructed, you can convert it to a string using
 *  the chirc_message_to_string function. For example:
 *
 *      char *str;
 *
 *      chirc_message_to_string(&msg, &str);
 *
 *  After this call, the str variable will point to a string containing
 *  the string representation of the message.
 */
#ifndef MESSAGE_H_
#define MESSAGE_H_

#include "chirc.h"

/*! \brief Construct a message starting from a string containing an IRC message
 *
 * \param msg Message. Must point to allocated memory.
 * \param s String containing an IRC message
 * \return 0 on success, non-zero if the message couldn't be parsed
 */
int chirc_message_from_string(chirc_message_t *msg, char *s);


/*! \brief Produces a string representation of the message
 *
 * \param msg Message.
 * \param s Pointer to a char* (the char* will be updated to
 *          point to the string representation of the message)
 * \return 0 on success, non-zero on failure
 */
int chirc_message_to_string(chirc_message_t *msg, char **s);


/*! \brief Constructs a message
 *
 * The message is constructed with the given prefix and command,
 * but no parameters.
 *
 * \param msg Message. Must point to allocated memory.
 * \param prefix Prefix (can be NULL)
 * \param cmd Command (cannot be NULL)
 * \return 0 on success, non-zero on failure
 */
int chirc_message_construct(chirc_message_t *msg, char *prefix, char *cmd);


/*! \brief Adds a parameter to a message
 *
 * \param msg Message.
 * \param param Parameter to add
 * \param longlast If true, the parameter is a "long parameter" and will be
 *        rendered with a ":" before it (note: only the last parameter can
 *        be a long parameter).
 * \return 0 on success, non-zero on failure
 */
int chirc_message_add_parameter(chirc_message_t *msg, char *param, bool longlast);


/*! \brief Constructs a reply
 *
 * Replies include information about the server and the recipient of the reply.
 * This function is a wrapper around chirc_message_construct and takes care
 * of setting the appropriate fields in the reply, up to and including
 * the reply code (but not the parameter replies, which need to be added
 * with chirc_message_add_parameter)
 *
 * \param msg Message. Must point to allocated memory.
 * \param ctx Server context
 * \param conn Connection the reply will be sent through (i.e., the peer
 *             we are replying to)
 * \param code 3-digit reply code
 * \return 0 on success, non-zero on failure
 */
int chirc_message_construct_reply(chirc_message_t *msg, chirc_ctx_t *ctx, chirc_connection_t *conn, char *code);


/*! \brief Frees a chirc_message_t struct
 *
 * This function frees memory allocated to the fields of a
 * chirc_message_t struct, but does not free the struct
 * itself (doing so is the responsibility of the caller
 * of this function)
 *
 * \param msg The message to free
 */
void chirc_message_free(chirc_message_t *msg);


#endif /* MESSAGE_H_ */
