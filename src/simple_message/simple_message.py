import logging
import sys
import os

from typing import List
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SimpleMessage:
    def __init__(
        self,
        token,
        destination_id="",
        msg_service_env_name="SIMPLE_MESSAGE_TYPE_DEFAULT",
        msg_service_override="",
        display_errors=True,
        log_filename="",
        logging_level="WARNING",
    ):
        """
            Constructor wrapper for message services such as slack.

        @param token: str, API token
        @param destination_id: str, intended for slack but of possible use in other services
            Must be specified in either constructor or send method or both to use slack
        @param msg_service_env_name: str, name of environment variable specifying the message service type. A default
            name has been provided to allow external code to instantiate the class without explicitly declaring a name
            for the purpose of external code maintainability should other services be added later.
        @param msg_service_override: str, possible values: 'slack'. Specifying this will override the type
            specified by the environment variable
        @param display_errors: boolean, whether to print API error messages. Most useful when sending logging
            output to a log file but in addition want to display errors to stdout
        @param log_filename: str, name of log file, optional
        @param logging_level: str, one of CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
        """
        self.token = token
        self.msg_type = ""
        self.channel_id = destination_id
        self.display_errors = display_errors  # display error message to stdout
        self.log_filename = log_filename  # name of log
        self.logging_level = logging_level

        self.valid_msg_services: List[str] = [
            "slack"
        ]  # TODO Update if additional services are added

        self.slack_msg = None

        self._setup_logging()

        if not self.token:
            self._log_error("Message requires a valid token")

        self._setup_service_type(msg_service_env_name, msg_service_override)

        if self.msg_type.lower() == "slack":
            self.slack_msg = _SlackMessage(
                token=self.token,
                channel_id=self.channel_id,
                display_errors=self.display_errors,
            )
        else:
            print("Only valid argument for msg_type implemented is: 'slack'")
            pass  # TODO as needed

    def _setup_service_type(self, msg_service_env_name, msg_service_override):
        msg_env_value = os.environ.get(msg_service_env_name)
        msg_env_value = msg_env_value.lower() if msg_env_value else ""
        msg_service_override = (
            msg_service_override.lower() if msg_service_override else ""
        )

        if (
            msg_service_override not in self.valid_msg_services
            and msg_env_value not in self.valid_msg_services
        ):
            error_msg = (
                "Must specify an environment variable name which contains the message service type or the"
                "service type in msg_service_override. Valid values to date for message service type are {}. "
                "If msg_service_override is specified then it will take precedence over the "
                "env variable setting.".replace("\n", "")
            ) + "\n"

            error_msg.format(", ".join([f'"{x}"' for x in self.valid_msg_services]))
            self._log_error(error_msg)
        elif msg_env_value in self.valid_msg_services:
            self.msg_type = msg_env_value
        elif msg_service_override in self.valid_msg_services:
            self.msg_type = msg_service_override
        else:
            self._log_error("Unable to determine message service type")

        if self.msg_type:
            print(f"Using {self.msg_type} service for messages")

    def send(self, msg_text, destination_id=None, **kwargs):
        """
            Send message method calls the appropriate message service
        @param msg_text: str, text of message
        @param destination_id: str, identifying id for slack or other similar services
        @param kwargs:
        @return: boolean
        """
        if self.msg_type == "slack":
            rv = self.slack_msg.send(
                msg_text=msg_text, channel_id=destination_id
            )  # returns SlackResponse object

            return rv.get("ok")  # returns boolean
        else:
            # for other messaging services
            return None

    def last_api_responses(self, n=1):
        """
            Return the objects returned by the last send message attempt API call
        @param n: int, last n objects in stack of responses
        @return: list, containing responses
        """
        func = sys._getframe().f_code.co_name
        error_msg = (
            f"argument for {func} must be int type. Using n=1 as default instead."
        )

        if isinstance(n, int):
            n *= -1
        elif isinstance(n, str):
            if n.isdigit():
                n = int(n) * -1
            else:
                n = -1
                logging.error(error_msg)
        else:
            n = -1
            logging.error(error_msg)

        if self.msg_type == "slack":
            return self.slack_msg.api_response_objects[n:]
        else:
            pass  # TODO when another service is implemented

    def last_api_response(self):
        """
        @return: object, the last api response only
        """
        responses = self.last_api_responses(n=1)
        return responses[0] if len(responses) > 0 else None

    def _setup_logging(self):
        if self.logging_level.upper() in [
            "CRITICAL",
            "ERROR",
            "WARNING",
            "INFO",
            "DEBUG",
            "NOTSET",
        ]:
            self.logging_level = self.logging_level.upper()
        else:
            print(
                "Invalid argument passed for logging level. Using WARNING by default. Please use one of "
                "CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET"
            )
            self.logging_level = "DEBUG"

        if self.log_filename:
            if not self.log_filename.endswith(".log"):
                self.log_filename = ".".join([self.log_filename, "log"])

            logging.basicConfig(
                filename=self.log_filename,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                level=self.logging_level,
            )
        else:
            logging.basicConfig(
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                level=self.logging_level,
            )

    def _log_error(self, error_msg):
        logging.error(error_msg)
        print(error_msg) if not self.log_filename else None


class _SlackMessage:
    def __init__(self, token, channel_id=None, display_errors=True):
        """
            Slack constructor
        @param token: str, API token
        @param channel_id: str
        @param display_errors: boolean, whether to print API error messages
        """
        self.token = token
        self.channel_id = channel_id
        self.display_errors = display_errors
        self.client = WebClient(token=self.token)
        self.last_api_response_object = {}
        self.api_response_objects = []

    def send(self, msg_text, channel_id):
        """
            Send message to slack channel
        @param msg_text: str, message text
        @param channel_id: str
        @return: slack response object
        """
        if not self.channel_id and not channel_id:
            error_msg = (
                "Message not attempted. A destination_id is required to use Slack "
                'for the following message: "%s". Set destination_id argument to your destination_id in '
                "either the constructor or the send() method." % msg_text
            )
            print(error_msg)
            logging.warning(error_msg)

            return {"ok": False}
        elif self.channel_id and not channel_id:
            channel_id = self.channel_id  # use the class level value

        try:
            self._add_api_response_to_list(
                self.client.chat_postMessage(channel=channel_id, text=msg_text)
            )
            logging.info(self.last_api_response_object)

            return self.last_api_response_object

        except SlackApiError as e:
            error_msg = f'Error posting the message "{msg_text}", Exception: {e}'
            logging.error(error_msg)

            if self.display_errors:
                print(error_msg)

            self._add_api_response_to_list(e.response)

            return self.last_api_response_object

        except Exception as e:
            error_msg = f"Error posting message {msg_text}, Exception: {e}"
            logging.error(error_msg)

            if self.display_errors:
                print(error_msg)

            return None

    def _add_api_response_to_list(self, response):
        """
            Add slack response object to list and update most recent response
        @param response: Slack response object
        """
        if response:
            self.api_response_objects.append(response)
            self.last_api_response_object = response


if __name__ == "__main__":
    # Simple Slack test
    msg_token = os.environ.get("SLACK_BOT_TOKEN")
    channel_id = os.environ.get("SLACK_CHANNEL_ID_DEMO")

    if not channel_id:
        raise ValueError("No channel_id found")
    if not msg_token:
        raise ValueError("No msg_token found")

    m = SimpleMessage(token=msg_token, destination_id=channel_id)
    rv = m.send("A test message from python")
