/*! \file utils.h
 *  \brief Utility functions
 *
 *  This module provides utility functions that are used across
 *  multiple modules.
 *
 *  If you need to implement a helper function that will be called
 *  from multiple modules, add it here. If the helper function is
 *  used in only one module, add it just to that module.
 */
#ifndef UTILS_H_
#define UTILS_H_

/* Add the declarations for your helper functions here,
 * and implement them in utils.c*/

/*! \brief Checks if a modes array contains a mode
 *
 * \param modes Modes array
 * \param mode Mode to check for
 * \return 1 if the array has the mode, 0 otherwise
 */
int has_mode(char *modes, char mode);


/*! \brief Adds a mode to a modes array
 *
 * This function has no effect if the user already
 * has the specified mode
 *
 * \param modes Modes array
 * \param mode Mode to add
 * \return 0 on success, non-zero on failure
 */
int set_mode(char *modes, char mode);


/*! \brief Removes a mode from a mode array
 *
 * \param modes Modes array
 * \param mode Mode to remove
 * \return 0 on success, non-zero on failure (particularly
 *         if the user does not have the specified mode)
 */
int remove_mode(char *modes, char mode);

#endif /* UTILS_H_ */
