import logging

from flask import g, current_app

from rocketchat_API.rocketchat import RocketChat
from ..actions.models import Action

logger = logging.getLogger()


def get_rocket():
    """ Create if doesn't exist or return edap from flask g object """
    if 'rocket' not in g:
        try:
            g.rocket = RocketChat(
                    current_app.config["ROCKETCHAT_USER"],
                    current_app.config["ROCKETCHAT_PASSWORD"],
                    server_url=current_app.config["ROCKETCHAT_HOST"])
            g.rocket_exception = None
        except Exception as e:
            g.rocket = None
            g.rocket_exception = e
    return g.rocket


class RocketMixin:

    @property
    def rocket(self):
        return get_rocket()


class RocketChatService(RocketMixin):

    def create_user(self, username, password, email, name):
        """
        Create user

        Args:
            username (str):
            password (str):
            email (str):
            name (str):

        Returns (response):

        """
        res = None
        success = False
        try:
            res = self.rocket.users_create(email, name, password, username, requirePasswordChange=True)
            if res.status_code == 200:
                success = True
        except Exception as e:
            logger.exception('Exception during user creation')
            success = False
        # TODO: what to do with password ?
        Action.create_event(event=Action.CREATE_ROCKET_USER,
                            success=success,
                            username=username,
                            email=email,
                            name=name)
        return res

    def create_channel(self, channel_name):
        """
        Create channel
        Args:
            channel_name (str):

        Returns:

        """
        res = None
        success = False
        try:
            res = self.rocket.channels_create(channel_name)
            if res.status_code == 200:
                success = True
        except Exception as e:
            logger.exception('Exception during channel creation')
            success = False
        Action.create_event(event=Action.CREATE_ROCKET_CHANNEL,
                            success=success,
                            channel_name=channel_name)
        return res

    def delete_user(self, user_id):
        return self.rocket.users_delete(user_id)

    def get_channel_by_name(self, channel_name):
        """ Get rocket channel json object by it's name """
        query = '{{"fname": {{"$eq": "{channel_name}"}}}}'.format(channel_name=channel_name)
        res = self.rocket.channels_list(query=query)
        if res.status_code != 200:
            return None
        channels = res.json()['channels']
        if not channels:
            return None
        return channels[0]

    def get_user_by_username(self, username):
        """ Get rocket user json object by it's username """
        res = self.rocket.users_list(query='{{"username":{{"$eq": "{username}"}}}}'.format(username=username))
        if res.status_code != 200:
            return None
        users = res.json()['users']
        if not users:
            return None
        return users[0]


rocket_service = RocketChatService()
