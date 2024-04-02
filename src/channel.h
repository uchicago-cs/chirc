/*! \file channel.h
 *  \brief Functions related to chirc_channel_t
 *
 *  This module provides functions related to the chirc_channel_t struct
 *  (defined in chirc.h).
 *
 *  An instance of a chirc_channel_t struct represents a channel in the
 *  server.
 *
 *  Note: Functions related to manipulating users in channels (e.g.,
 *  adding a user to a channel, checking whether a user is in a channel,
 *  etc.) can be found in channeluser.h
 */

#ifndef CHANNEL_H_
#define CHANNEL_H_

#include "chirc.h"

/*! \brief Initializes a chirc_channel_t struct
 *
 * This function assumes that memory has already been allocated
 * for the struct, and will initialize its fields.
 *
 * \param channel The channel to initialize
 */
void chirc_channel_init(chirc_channel_t *channel);


/*! \brief Frees a chirc_channel_t struct
 *
 * This function frees memory allocated to the fields of a
 * chirc_channel_t struct, but does not free the struct
 * itself (doing so is the responsibility of the caller
 * of this function)
 *
 * \param channel The channel to free
 */
void chirc_channel_free(chirc_channel_t *channel);


/*! \brief Checks if a channel has a given mode
 *
 * \param channel Channel
 * \param mode Mode
 * \return 1 if the channel has the mode, 0 otherwise
 */
int chirc_channel_has_mode(chirc_channel_t *channel, char mode);


/*! \brief Adds a mode to a channel
 *
 * This function has no effect if the channel already
 * has the specified mode
 *
 * \param channel Channel
 * \param mode Mode
 * \return 0 on success, non-zero on failure
 */
int chirc_channel_set_mode(chirc_channel_t *channel, char mode);


/*! \brief Removes a mode from a channel
 *
 * \param channel Channel
 * \param mode Mode
 * \return 0 on success, non-zero on failure (particularly
 *         if the channel does not have the specified mode)
 */
int chirc_channel_remove_mode(chirc_channel_t *channel, char mode);


/*! \brief Returns the number of users in the channel
 *
 * \param channel Channel
 * \return Number of users in the channel
 */
int chirc_channel_num_users(chirc_channel_t *channel);


#endif /* CHANNEL_H_ */
