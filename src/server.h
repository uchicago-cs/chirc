/*! \file server.h
 *  \brief Functions related to chirc_server_t
 *
 *  This module provides functions related to the chirc_server_t struct.
 *
 *  It currently only includes functions for initializing and destroying
 *  a chirc_server_t struct.
 *
 */
#ifndef SERVER_H_
#define SERVER_H_

#include "chirc.h"

/*! \brief Initializes a chirc_server_t struct
 *
 * This function assumes that memory has already been allocated
 * for the struct, and will initialize its fields.
 *
 * \param server The server to initialize
 */
void chirc_server_init(chirc_server_t *server);


/*! \brief Frees a chirc_server_t struct
 *
 * This function frees memory allocated to the fields of s
 * chirc_server_t struct, but does not free the struct
 * itself (doing so is the responsibility of the caller
 * of this function)
 *
 * \param server The server to free
 */
void chirc_server_free(chirc_server_t *server);

#endif /* SERVER_H_ */
