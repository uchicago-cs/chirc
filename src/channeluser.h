/*! \file channel.h
 *  \brief Functions related to chirc_channeluser_t
 *
 *  This module provides functions related to the chirc_channeluser_t struct
 *  (defined in chirc.h).
 *
 *  An instance of a chirc_channeluser_t struct contains information
 *  about user in a channel.
 */

#ifndef CHANNELUSER_H_
#define CHANNELUSER_H_

#include "chirc.h"

/*! \brief Initializes a chirc_channeluser_t struct
 *
 * This function assumes that memory has already been allocated
 * for the struct, and will initialize its fields.
 *
 * \param channeluser The channeluser struct to initialize
 */
void chirc_channeluser_init(chirc_channeluser_t *channeluser);


/*! \brief Frees a chirc_channeluser_t struct
 *
 * This function frees memory allocated to the fields of a
 * chirc_channeluser_t struct, but does not free the struct
 * itself (doing so is the responsibility of the caller
 * of this function)
 *
 * \param channeluser The channeluser struct to free
 */
void chirc_channeluser_free(chirc_channeluser_t *channeluser);


/*! \brief Checks if a user in a channel has a given mode
 *
 * \param channeluser User-in-Channel
 * \param mode Mode
 * \return 1 if the channel has the mode, 0 otherwise
 */
int chirc_channeluser_has_mode(chirc_channeluser_t *channeluser, char mode);


/*! \brief Adds a mode to a user in a channel
 *
 * This function has no effect if the user already
 * has the specified mode in that channel
 *
 * \param channeluser User-in-Channel
 * \param mode Mode
 * \return 0 on success, non-zero on failure
 */
int chirc_channeluser_set_mode(chirc_channeluser_t *channeluser, char mode);


/*! \brief Removes a mode from a user in a channel
 *
 * \param channeluser User-in-Channel
 * \param mode Mode
 * \return 0 on success, non-zero on failure (particularly
 *         if the user does not have the specified mode
 *         in that channel)
 */
int chirc_channeluser_remove_mode(chirc_channeluser_t *channeluser, char mode);


/*!
 * \brief Get the chirc_channeluser_t struct corresponding to a user in a channel
 *
 * \param channel Channel
 * \param user User
 * \return If the user is in a channel, returns the chirc_channeluser_t struct.
 *         Otherwise, returns NULL
 */
chirc_channeluser_t* chirc_channeluser_get(chirc_channel_t *channel, chirc_user_t *user);


/*!
 * \brief Get or create a chirc_channeluser_t struct.
 *
 * If the specified user is already in the channel, return the
 * chirc_channeluser_t correspnding to that user in the channel.
 * Otherwise, create a chirc_channeluser_t struct, and add it
 * to the users and channels hash tables (in the channel and user,
 * respectively)
 *
 * \param channel Channel
 * \param user User
 * \param channeluser (Output parameter) User-in-Channel
 * \return True if the chirc_channeluser_t was created (i.e., if the user
 *         was not already in the channel). False otherwise (i.e., if the
 *         user was already in the channel)
 */
bool chirc_channeluser_get_or_create(chirc_channel_t *channel, chirc_user_t *user, chirc_channeluser_t **channeluser);


/*!
 * \brief Remove a channel-user association
 *
 * This will remove the channeluser from the user's
 * channels hash table, and from the channel's hash
 * table. It does not free the channeluser struct,
 * nor does it perform other operations associated
 * with a user leaving a channel (like relaying a PART
 * or QUIT message)
 *
 * \param channeluser User-in-Channel
 * \return 0 on success, non-zero on failure
 */
int chirc_channeluser_remove(chirc_channeluser_t *channeluser);

#endif /* CHANNELUSER_H_ */
