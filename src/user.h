/*! \file user.h
 *  \brief Functions related to chirc_user_t
 *
 *  This module provides functions related to the chirc_user_t struct
 *  (defined in chirc.h).
 *
 *  An instance of a chirc_user_t struct represents a user connected
 *  to the server.
 */
#ifndef USER_H_
#define USER_H_

#include "chirc.h"


/*! \brief Initializes a chirc_user_t struct
 *
 * This function assumes that memory has already been allocated
 * for the struct, and will initialize its fields.
 *
 * \param user The user to initialize
 */
void chirc_user_init(chirc_user_t *user);


/*! \brief Frees a chirc_user_t struct
 *
 * This function frees memory allocated to the fields of a
 * chirc_user_t struct, but does not free the struct
 * itself (doing so is the responsibility of the caller
 * of this function)
 *
 * \param user The user to free
 */
void chirc_user_free(chirc_user_t *user);


/*! \brief Checks if a user has a given mode
 *
 * \param user User
 * \param mode Mode
 * \return 1 if the user has the mode, 0 otherwise
 */
int chirc_user_has_mode(chirc_user_t *user, char mode);


/*! \brief Adds a mode to a user
 *
 * This function has no effect if the user already
 * has the specified mode
 *
 * \param user User
 * \param mode Mode
 * \return 0 on success, non-zero on failure
 */
int chirc_user_set_mode(chirc_user_t *user, char mode);


/*! \brief Removes a mode from a user
 *
 * \param user User
 * \param mode Mode
 * \return 0 on success, non-zero on failure (particularly
 *         if the user does not have the specified mode)
 */
int chirc_user_remove_mode(chirc_user_t *user, char mode);


/*! \brief Checks if a user is an IRC operator
 *
 * \param user User
 * \return 1 if the user is an IRC operator, 0 otherwise
 */
int chirc_user_is_oper(chirc_user_t *user);


/*! \brief Returns the number of channels the user is in
 *
 * \param user User
 * \return Number of channels the user is in
 */
int chirc_user_num_channels(chirc_user_t *user);

#endif /* USER_H_ */
