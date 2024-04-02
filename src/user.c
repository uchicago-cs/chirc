/* See user.h for details about the functions in this module */

#include <stdio.h>
#include <string.h>
#include <assert.h>
#include "ctx.h"
#include "user.h"
#include "message.h"
#include "utils.h"
#include "connection.h"

/* See user.h */
void chirc_user_init(chirc_user_t *user)
{
    user->nick = NULL;
    user->username = NULL;
    user->fullname = NULL;
    user->modes[0] = '\0';
    user->awaymsg = NULL;
    user->server = NULL;
    user->registered = false;

    user->channels = NULL;
}


/* See user.h */
void chirc_user_free(chirc_user_t *user)
{
    sdsfree(user->nick);
    sdsfree(user->username);
    sdsfree(user->fullname);
    sdsfree(user->awaymsg);

    /* We shouldn't free a user until all their channels
     * have been removed */
    assert(user->channels == NULL);
}


/* See user.h */
int chirc_user_has_mode(chirc_user_t *user, char mode)
{
    int rc;

    rc = has_mode(user->modes, mode);

    return rc;
}


/* See user.h */
int chirc_user_set_mode(chirc_user_t *user, char mode)
{
    int rc;

    rc = set_mode(user->modes, mode);

    return rc;
}


/* See user.h */
int chirc_user_remove_mode(chirc_user_t *user, char mode)
{
    int rc;

    rc = remove_mode(user->modes, mode);

    return rc;
}


/* See user.h */
int chirc_user_is_oper(chirc_user_t *user)
{
    return chirc_user_has_mode(user, 'o');
}


/* See user.h */
int chirc_user_num_channels(chirc_user_t *user)
{
    return HASH_CNT(hh_from_user, user->channels);
}