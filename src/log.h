/*! \file log.h
 *  \brief Logging functions
 *
 *  Use these functions to print log messages. Each message has an
 *  associated log level:
 *
 *  CRITICAL: A critical unrecoverable error
 *  ERROR: A recoverable error
 *  WARNING: A warning
 *  INFO: High-level information about the progress of the application
 *  DEBUG: Lower-level information
 *  TRACE: Very low-level information.
 *
 */

#ifndef CHIRC_LOG_H_
#define CHIRC_LOG_H_

#include "connection.h"

/*! \brief Log levels */
typedef enum {
    QUIET    = 00,
    CRITICAL = 10,
    ERROR    = 20,
    WARNING  = 30,
    INFO     = 40,
    DEBUG    = 50,
    TRACE    = 60
} loglevel_t;

/*! \brief Sets the logging level
 *
 * When a log level is set, all messages at that level or "worse" are
 * printed. e.g., if you set the log level to WARNING, then all
 * WARNING, ERROR, and CRITICAL messages will be printed.
 *
 * \param level  Logging level
 */
void chirc_setloglevel(loglevel_t level);

/*! \brief Print a log message
 *
 * \param level Logging level of the message
 * \param fmt printf-style formatting string
 * \param ... Extra parameters if needed by fmt
 */
void chilog(loglevel_t level, char *fmt, ...);

/*! \brief Convenience function for logging information related to a connection
 *
 * This function is a wrapper around chilog, and will include useful information
 * about a connection in the log message.
 *
 * \param level Logging level of the message
 * \param conn Connection
 * \param fmt printf-style formatting string
 * \param ... Extra parameters if needed by fmt
 */
void serverlog(loglevel_t level, chirc_connection_t *conn, char *fmt, ...);

#endif /* CHIRC_LOG_H_ */
