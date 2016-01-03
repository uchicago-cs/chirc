/*
 *  Logging functions
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

/* Log levels */
typedef enum {
    QUIET    = 00,
    CRITICAL = 10,
    ERROR    = 20,
    WARNING  = 30,
    INFO     = 40,
    DEBUG    = 50,
    TRACE    = 60
} loglevel_t;

/*
 * chitcp_setloglevel - Sets the logging level
 *
 * When a log level is set, all messages at that level or "worse" are
 * printed. e.g., if you set the log level to WARNING, then all
 * WARNING, ERROR, and CRITICAL messages will be printed.
 *
 * level: Logging level
 *
 * Returns: Nothing.
 */
void chirc_setloglevel(loglevel_t level);


/*
 * chilog - Print a log message
 *
 * level: Logging level of the message
 *
 * fmt: printf-style formatting string
 *
 * ...: Extra parameters if needed by fmt
 *
 * Returns: nothing.
 */
void chilog(loglevel_t level, char *fmt, ...);


#endif /* CHIRC_LOG_H_ */
