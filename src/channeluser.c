/* See channeluser.h for details about the functions in this module */

#include <string.h>
#include <pthread.h>
#include "channeluser.h"
#include "utils.h"


/* See channeluser.h */
void chirc_channeluser_init(chirc_channeluser_t *channeluser)
{
    channeluser->user = NULL;
    channeluser->channel = NULL;
    channeluser->modes[0] = '\0';
}


/* See channeluser.h */
int chirc_channeluser_has_mode(chirc_channeluser_t *channeluser, char mode)
{
    int rc;

    rc = has_mode(channeluser->modes, mode);

    return rc;
}


/* See channeluser.h */
int chirc_channeluser_set_mode(chirc_channeluser_t *channeluser, char mode)
{
    int rc;

    rc = set_mode(channeluser->modes, mode);

    return rc;
}


/* See channeluser.h */
int chirc_channeluser_remove_mode(chirc_channeluser_t *channeluser, char mode)
{
    int rc;

    rc = remove_mode(channeluser->modes, mode);

    return rc;
}


/* See channeluser.h */
chirc_channeluser_t* chirc_channeluser_get(chirc_channel_t *channel, chirc_user_t *user)
{
    chirc_channeluser_t *channeluser;

    HASH_FIND(hh_from_channel,channel->users, &user,sizeof(chirc_user_t *), channeluser);

    return channeluser;
}


/* See channeluser.h */
bool chirc_channeluser_get_or_create(chirc_channel_t *channel, chirc_user_t *user, chirc_channeluser_t **channeluser)
{
    bool created;

    HASH_FIND(hh_from_channel,channel->users, &user,sizeof(chirc_user_t *), *channeluser);
    if(*channeluser)
    {
        created = false;
    }
    else
    {
        created = true;

        *channeluser = malloc(sizeof(chirc_channeluser_t));
        chirc_channeluser_init(*channeluser);
        (*channeluser)->channel = channel;
        (*channeluser)->user = user;
        HASH_ADD(hh_from_user, user->channels, channel, sizeof(chirc_channel_t *), *channeluser);
        HASH_ADD(hh_from_channel, channel->users, user, sizeof(chirc_user_t *), *channeluser);
    }

    return created;
}