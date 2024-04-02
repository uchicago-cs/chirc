/* See channel.h for details about the functions in this module */

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>
#include "message.h"
#include "connection.h"
#include "channel.h"
#include "utils.h"
#include "chirc.h"

/* See channel.h */
void chirc_channel_init(chirc_channel_t *channel)
{
    channel->name = NULL;
    channel->topic = NULL;
    channel->modes[0] = '\0';

    channel->users = NULL;
}


/* See channel.h */
void chirc_channel_free(chirc_channel_t *channel)
{
    sdsfree(channel->name);
    sdsfree(channel->topic);

    /* Should only be called when all users have left the channel */
    assert(channel->users == NULL);
}


/* See channel.h */
int chirc_channel_has_mode(chirc_channel_t *channel, char mode)
{
    int rc;

    rc = has_mode(channel->modes, mode);

    return rc;
}


/* See channel.h */
int chirc_channel_set_mode(chirc_channel_t *channel, char mode)
{
    int rc;

    rc = set_mode(channel->modes, mode);

    return rc;
}


/* See channel.h */
int chirc_channel_remove_mode(chirc_channel_t *channel, char mode)
{
    int rc;

    rc = remove_mode(channel->modes, mode);

    return rc;
}

/* See channel.h */
int chirc_channel_num_users(chirc_channel_t *channel)
{
    return HASH_CNT(hh_from_channel, channel->users);
}


