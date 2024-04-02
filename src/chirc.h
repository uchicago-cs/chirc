/*! \file chirc.h
 *  \brief chirc data structures
 *
 *  This module specifies several structs that are used throughout
 *  the server.
 *
 *  - chirc_message_t: An IRC message
 *  - chirc_server_t: An IRC server in an IRC Network
 *  - chirc_user_t: A user connected to an IRC server
 *  - chirc_connection_t: A connection to an IRC server
 *  - chirc_channel_t: A channel in an IRC server
 *  - chirc_channeluser_t: Represents the presence of a user
 *    in a channel
 *  - chirc_ctx_t: Server context
 *
 *  The best way to read this file is to start by looking at
 *  chirc_ctx_t. This is the "server context": it contains
 *  all the global state of the server, and it is passed to
 *  practically all functions.
 *
 */

#ifndef CHIRC_H_
#define CHIRC_H_

#include <sds.h>
#include <uthash.h>
#include <stdbool.h>
#include <pthread.h>

/*! Maximum size of an IRC message */
#define MSG_MAX (512)

/*! Function return value: success */
#define CHIRC_OK (0)

/*! Function return value: failure */
#define CHIRC_FAIL (-1)

/*! Server version */
#define VERSION "chirc-0.6.0"

/*! Supported user modes */
#define USERMODES "ao"

/*! Supported channel modes */
#define CHANNELMODES "mt"

/*! Supported user-in-channel modes */
#define CHANNELUSERMODES "ov"

/* Forward declarations */
typedef struct chirc_connection chirc_connection_t;
typedef struct chirc_channeluser chirc_channeluser_t;

/*! \struct chirc_message_t
 * \brief An IRC message
 *
 * This struct represents a single IRC message. To create/update
 * this struct, use the functions provided in message.h.
 */
typedef struct {
    /*! \brief Prefix. NULL if there is no prefix. */
    char *prefix;

    /*! \brief Command (NICK, USER, PRIVMSG, ...) */
    char *cmd;

    /*! \brief Command parameters */
    char *params[15];

    /*! \brief Number of parameters */
    unsigned int nparams;

    /*! \brief Is the last parameter a long parameter?
     *
     * If true, indicates that the last parameter is a long
     * parameter, and would be rendered with a ":" before it.
     */
    bool longlast;

    /*! \brief The raw contents of the message */
    char *raw;
} chirc_message_t;


/*! \struct chirc_server_t
 * \brief An IRC server in an IRC Network
 *
 * This struct represents a server in an IRC network.
 *
 * When the server runs in standalone mode, a single
 * chirc_server_t struct is created in the network.this_server
 * field of chirc_ctx_t, and only the
 * hostname and port fields are initialized.
 *
 * When the server runs in network mode, we create
 * one chirc_server_t struct for each server in the network,
 * which we can access through the network.servers hash table
 * in chirc_ctx_t.
 */
typedef struct
{
    /*! \brief Server identifier
     *
     *  This is a name that uniquely identifies the server. While a
     *  hostname is typically used, you should not treat it like a
     *  hostname (i.e., you should not try to connect to a server
     *  via its server name). The server name should be treated
     *  as a string identifier.
     *
     *  Only used when running in network mode.
     * */
    sds servername;

    /*! \brief The hostname or IP address that we can use to connect to the server.
     *
     * For the currently running server, this will be the server's hostname
     * (as returned by gethostname) */
    sds hostname;

    /*! \brief The port we can use to connect to the server.
     *
     * For the currently running server, this will be the port the server
     * listens on */
    sds port;

    /*! \brief Password to connect to the server
     *
     * Only used when running in network mode
     * */
    sds passwd;

    /*! \brief Has the connection been successfully registered?
     *
     * Only used when running in network mode
     *
     */
    bool registered;

    /*! \brief Connection to the server
     *
     * Only used when running in network mode. */
    chirc_connection_t *conn;

    /*! \brief uthash handle
     *
     * Only used when running in network mode */
    UT_hash_handle hh;
} chirc_server_t;


/*! \struct chirc_user_t
 * \brief A user connected to an IRC server
 */
typedef struct
{
    /*! \brief The user's nick */
	sds nick;

    /*! \brief The user's username */
	sds username;

    /*! \brief The user's full name */
	sds fullname;

    /*! \brief The hostname the user is connecting from */
    sds hostname;

    /*! \brief Has the user fully registered with the server */
    bool registered;

    /*! \brief User modes
     *
     * This string-like array contains one character for
     * each mode enabled in the user. Use the functions
     * defined in utils.h to manipulate this array.
     * */
	char modes[10];

    /*! \brief Away message
     *
     * NULL if the user is not away.
     */
	sds awaymsg;

    /*! \brief Server the user is connected to.
     *
     * In standalone mode, this will always be a pointer
     * to network.this_server in the chirc_ctx_t struct.
     */
    chirc_server_t *server;

    /*! \brief Hash table of channels the user has joined.
     *
     * Note how the hash table uses chirc_channeluser_t structs
     * instead of chirc_channel_t structs. This is because a user
     * can have modes that are specific to a channel, and this
     * is tracked via the chirc_channeluser_t struct.
     */
    chirc_channeluser_t *channels;

    /*! \brief Connection corresponding to this user */
    chirc_connection_t *conn;

    /*! \brief uthash handle
     *
     * This is used by the users hash table in chirc_ctx_t
     */
    UT_hash_handle hh;
} chirc_user_t;


/*! \brief Connection type
 *
 * When a peer first connects to the server, the connection
 * starts in an UNKNOWN state (we don't yet know if it's a user
 * or a server). Based on the commands sent by the peer,
 * we will flag the connection as USER (if we receive USER and NICK
 * commands) or as SERVER (if we receive SERVER and PASS commands)
 * */
typedef enum
{
    CONN_TYPE_UNKNOWN = 0,
    CONN_TYPE_USER = 1,
    CONN_TYPE_SERVER = 2
} conn_type_t;


/*! \struct chirc_connection_t
 * \brief A connection to an IRC server
 */
typedef struct chirc_connection
{
    /*! \brief Type of connection */
    conn_type_t type;

    /*! \brief A connection corresponds to either a user or a server */
    union {
        /*! \brief User on the other end of the connection */
        chirc_user_t *user;

        /*! \brief Server on the other end of the connection */
        chirc_server_t *server;
    } peer;

    /*! \brief Peer's hostname */
    sds hostname;

    /*! \brief Peer's port */
    sds port;

    /*! \brief Socket for the connection */
    int socket;

    /*! \brief uthash handle
     *
     * Used by the connections hash table in chirc_ctx_t */
    UT_hash_handle hh;
} chirc_connection_t;


/*! \struct chirc_channel_t
 * \brief A channel in an IRC server
 */
typedef struct
{
    /*! \brief Channel name */
	sds name;

    /*! \brief Channel topic */
	sds topic;

    /*! \brief Channel modes
     *
     * This string-like array contains one character for
     * each mode enabled in the channel. Use the functions
     * defined in utils.h to manipulate this array. */
	char modes[10];

    /*! \brief Hash table of users in the channel.
     *
     * Note how the hash table uses chirc_channeluser_t structs
     * instead of chirc_user_t structs. This is because a user
     * can have modes that are specific to a channel, and this
     * is tracked via the chirc_channeluser_t struct.
     */
    chirc_channeluser_t *users;

    /*! \brief uthash handle
     *
     * Used by the channels hash table in chirc_ctx_t */
    UT_hash_handle hh;
} chirc_channel_t;


/*! \struct chirc_channeluser_t
 * \brief Represents the presence of a user in a channel
 *
 * We define this separate struct because users have channel-specific
 * modes (separate from their user modes). If we needed to keep track
 * of any other channel-specific information for a user, we could also
 * put it in this struct.
 */
typedef struct chirc_channeluser
{
    /*! \brief User */
    chirc_user_t *user;

    /*! \brief Channel */
    chirc_channel_t *channel;

    /*! \brief Channel-specific modes for user
     *
     * This string-like array contains one character for
     * each mode enabled for the user in the channel. Use
     * the functions defined in utils.h to manipulate this
     * array. */
    char modes[10];

    /*! \brief uthash handle (for chirc_user_t)
     *
     * Used by the channels hash table in chirc_user_t */
    UT_hash_handle hh_from_user;

    /*! \brief uthash handle (for chirc_channel_t)
     *
     * Used by the users hash table in chirc_channel_t */
    UT_hash_handle hh_from_channel;
} chirc_channeluser_t;


/*! \struct chirc_ctx_t
 * \brief Server context
 *
 * This struct contains all the global information in the server.
 * Basically, all the information in the server (such as the users
 * and channels) can be accessed starting from this struct.
 *
 * To create/update this struct, use the functions provided in ctx.h.
 * */
typedef struct
{
    /*! \brief Operator password */
    sds oper_passwd;

    /*! \brief Hash table of channels */
    chirc_channel_t *channels;

    /*! \brief Hash table of users */
    chirc_user_t *users;

    /*! \brief IRC network
     *
     * When running in standalone mode, the servers
     * field is set to NULL, and this_server contains
     * information about the server we are running
     * (minus information that is only relevant in
     * IRC networks; see chirc_server_t for more details)
     *
     * When running in network mode, servers is a hash
     * table providing access to information about all
     * the servers in the network. */
    struct {
        /*! \brief Information about the running server */
        chirc_server_t *this_server;

        /*! \brief Servers in the IRC Network */
        chirc_server_t *servers;
    } network;

    /*! \brief Server version */
    sds version;

    /*! \brief Date/time the server started running */
    struct tm created;

    /*! \brief Hash table of connections into the server*/
    chirc_connection_t *connections;
} chirc_ctx_t;

#endif /* CHIRC_H_ */
