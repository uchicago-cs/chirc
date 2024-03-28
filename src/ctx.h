/*! \file ctx.h
 *  \brief Functions related to chirc_ctx_t
 *
 *  This module provides functions related to the chirc_ctx_t struct
 *  (defined in chirc.h)
 *
 *  This struct contains all the global information in the server.
 *  Basically, all the information in the server (such as the users
 *  and channels) can be accessed starting from this struct. This
 *  module provides some convenience functions for updating/accessing
 *  the information contained in the struct.
 */

#ifndef CTX_H_
#define CTX_H_

#include "chirc.h"

/*! \brief Initializes a chirc_ctx_t struct
 *
 * This function assumes that memory has already been allocated
 * for the struct, and will initialize its fields.
 *
 * \param conn The context to initialize
 */
void chirc_ctx_init(chirc_ctx_t *ctx);


/*! \brief Frees a chirc_ctx_t struct
 *
 * This function frees memory allocated to the fields of a
 * chirc_ctx_t struct, but does not free the struct
 * itself (doing so is the responsibility of the caller
 * of this function)
 *
 * \param conn The context to free
 */
void chirc_ctx_free(chirc_ctx_t *ctx);


/*! \brief Adds a connection to the server context
 *
 * \param ctx Server context
 * \param conn The connection to add
 */
void chirc_ctx_add_connection(chirc_ctx_t *ctx, chirc_connection_t *conn);


/*! \brief Removes a connection from the server context
 *
 * \param ctx Server context
 * \param conn The connection to add
 */
void chirc_ctx_remove_connection(chirc_ctx_t *ctx, chirc_connection_t *conn);


/*! \brief Gets the number of registered users in the server
 *
 * Note that this function will exclude connections that haven't
 * completed a user registration (i.e., successfully sending
 * a USER and NICK command)
 *
 * \param ctx Server context
 * \return Number of users in the server
 */
int chirc_ctx_numusers(chirc_ctx_t *ctx);


/*! \brief Gets the number of IRC Operators in the server
 *
 * \param ctx Server context
 * \return Number of IRC Operators in the server
 */
int chirc_ctx_numops(chirc_ctx_t *ctx);


/*! \brief Gets the number of channels in the server
 *
 * \param ctx Server context
 * \return Number of channels in the server
 */
int chirc_ctx_numchannels(chirc_ctx_t *ctx);


/*! \brief Gets the number of unknown connections in the server
 *
 * An unknown connection is an active connection to the server
 * that has not yet completed either a user (USER+NICK) or
 * server (SERVER+PASS) registration.
 *
 * \param ctx Server context
 * \return Number of unknown connections in the server
 */
int chirc_ctx_unknown_connections(chirc_ctx_t *ctx);


/*!
 * \brief Get a channel with a given name (if one exists)
 * \param ctx Server context
 * \param channelname Channel name
 * \return The channel, if one exists. Otherwise, returns NULL.
 */
chirc_channel_t* chirc_ctx_get_channel(chirc_ctx_t *ctx, char *channelname);


/*!
 * \brief Get or create a channel.
 *
 * If a channel with the specified name already exists,
 * returns the corresponding chirc_channel_t struct.
 * Otherwise, creates a chirc_channel_t struct, initializes it,
 * (including setting its name to the provided value),
 * and adds it to the channels hash table.
 *
 * \param ctx Server context
 * \param channelname Channel name
 * \param channel (Output parameter) Channel
 * \return True if the chirc_channel_t was created (i.e., if the channel
 *         did not already exist). False otherwise (i.e., if there
 *         was already a channel with the given name)
 */
bool chirc_ctx_get_or_create_channel(chirc_ctx_t *ctx, char *channelname, chirc_channel_t **channel);


/*!
 * \brief Remove a channel from the server
 *
 * This only removes the channel from the channels hash table.
 * It does not perform any operations on the channel itself
 * (e.g., it does not clear the list of users in the channel, etc.)
 *
 * \param ctx Server
 * \param channel Channel
 * \return 0 on success, non-zero on failure
 */
int chirc_ctx_remove_channel(chirc_ctx_t *ctx, chirc_channel_t *channel);


/*!
 * \brief Get a user with a given nick (if one exists)
 * \param ctx Server context
 * \param nick User's nick
 * \return The channel, if one exists. Otherwise, returns NULL.
 */
chirc_user_t* chirc_ctx_get_user(chirc_ctx_t *ctx, char *nick);


/*!
 * \brief Get or create a user.
 *
 * If a user with the specified nick already exists,
 * returns the corresponding chirc_user_t struct.
 * Otherwise, creates a chirc_user_t struct, initializes it,
 * (including setting its nick to the provided value),
 * and adds it to the users hash table.
 *
 * \param ctx Server context
 * \param nick User nick
 * \param user (Output parameter) User
 * \return True if the chirc_user_t was created (i.e., if the user
 *         did not already exist). False otherwise (i.e., if there
 *         was already a user with the given nick)
 */
bool chirc_ctx_get_or_create_user(chirc_ctx_t *ctx, char *nick, chirc_user_t **user);


/*!
 * \brief Remove a user from the server
 *
 * This only removes the user from the users hash table.
 * It does not perform any operations on the user itself
 * (e.g., it does not clear the list of channels the user is in, etc.)
 *
 * \param ctx Server
 * \param user User
 * \return 0 on success, non-zero on failure
 */
int chirc_ctx_remove_user(chirc_ctx_t *ctx, chirc_user_t *user);


/*! \brief Loads a network specification into the server context
 *
 * The network file is a CSV file like this:
 *
 *    irc-1.example.net,127.0.0.1,6667,pass1
 *    irc-2.example.net,127.0.0.1,6668,pass2
 *
 *    Each row corresponds to one server, and contains the following
 *    fields:
 *
 *    - Server name (e.g., irc-1.example.net): A name that uniquely
 *      identifies the server. While a hostname is typically used,
 *      you should not treat it like a hostname (i.e., you should
 *      not try to connect to a server via its server name).
 *      The server name should be treated as a string identifier.
 *    - Hostname or IP address (e.g., 127.0.0.1): The hostname or
 *      IP address that we can use to connect to the server.
 *    - Port (e.g., 6667): The port we can use to connect to the server.
 *    - Server Password (e.g., pass1): Each server has an associated
 *      password. Other servers must supply this password to connect
 *      to the server.
 *
 * \param ctx Server context
 * \param file Path of network file
 * \param servername Name of the running server
 * \return 0 on success, non-zero on failure
 */
int chirc_ctx_load_network(chirc_ctx_t *ctx, char *file, char *servername);

#endif /* CTX_H_ */
