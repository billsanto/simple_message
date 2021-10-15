import unittest
import os
import sys

from simple_message import simple_message as msg


class SimpleMessageTestCase(unittest.TestCase):
    msg_token = os.environ.get('SLACK_BOT_TOKEN')
    channel_id = os.environ.get('SLACK_CHANNEL_ID_DEMO')
    channel_id2 = os.environ.get('SLACK_CHANNEL_ID_DEMO2')

    def test_msg_token(self):
        self.assertIsNotNone(self.msg_token)

    def test_channel_id(self):
        self.assertIsNotNone(self.channel_id)

    def test_channel_id2(self):
        self.assertIsNotNone(self.channel_id2)

    def test_message_with_global_channel_id(self):
        func = sys._getframe().f_code.co_name
        m = msg.SimpleMessage(token=self.msg_token, destination_id=self.channel_id)
        rv = m.send(f'Python unit test, {func}')

        self.assertTrue(rv)

    def test_message_with_send_channel_id(self):
        func = sys._getframe().f_code.co_name
        m = msg.SimpleMessage(token=self.msg_token)
        rv = m.send(f'Python unit test, {func}', destination_id=self.channel_id)

        self.assertTrue(rv)

    def test_message_with_send_channel_id_override(self):
        func = sys._getframe().f_code.co_name
        m = msg.SimpleMessage(token=self.msg_token, destination_id=self.channel_id)
        rv = m.send(f'Python unit test, {func}', destination_id=self.channel_id2)
        ro = m.last_api_response()

        self.assertTrue(rv)
        self.assertEqual(self.channel_id2, ro['channel'])

    def test_message_with_bad_global_channel_id(self):
        func = sys._getframe().f_code.co_name
        bad_channel_id = 'xyz'

        m = msg.SimpleMessage(token=self.msg_token, destination_id=bad_channel_id)
        rv = m.send(f'Python unit test, {func}')
        ro = m.last_api_response()

        self.assertFalse(rv)
        self.assertEqual('channel_not_found', ro['error'])

    def test_message_with_bad_send_channel_id(self):
        func = sys._getframe().f_code.co_name
        bad_channel_id = 'xyz'

        m = msg.SimpleMessage(token=self.msg_token)
        rv = m.send(f'Python unit test, {func}', destination_id=bad_channel_id)
        ro = m.last_api_response()

        self.assertFalse(rv)
        self.assertEqual('channel_not_found', ro['error'])

    def test_message_with_no_channel_id(self):
        func = sys._getframe().f_code.co_name
        bad_channel_id = ''

        m = msg.SimpleMessage(token=self.msg_token)
        rv = m.send(f'Python unit test, {func}', destination_id=bad_channel_id)
        ro = m.last_api_response()

        self.assertFalse(rv)
        # self.assertEqual(ro['error'], 'invalid_arguments')
        # self.assertEqual(ro['response_metadata']['messages'][0], '[ERROR] missing required field: channel')

    def test_message_with_bad_token(self):
        func = sys._getframe().f_code.co_name
        bad_token_id = 'xyz'

        m = msg.SimpleMessage(token=bad_token_id)
        rv = m.send(f'Python unit test, {func}', destination_id=self.channel_id)
        ro = m.last_api_response()

        self.assertFalse(rv)
        self.assertEqual('invalid_auth', ro.get('error'))

    def test_message_with_no_token(self):
        # Ref: https://izziswift.com/how-to-properly-use-unit-testings-assertraises-with-nonetype-objects/
        self.assertRaises(TypeError, lambda: msg.SimpleMessage())

    def test_message_with_empty_token(self):
        func = sys._getframe().f_code.co_name
        bad_token_id = ''

        m = msg.SimpleMessage(token=bad_token_id)
        rv = m.send(f'Python unit test, {func}', destination_id=self.channel_id)
        ro = m.last_api_response()

        self.assertFalse(rv)
        self.assertEqual('not_authed', ro.get('error'))

    def test_multiple_message_response_objects_with_global_channel_id(self):
        func = sys._getframe().f_code.co_name
        m = msg.SimpleMessage(token=self.msg_token, destination_id=self.channel_id)

        for i in range(2):
            m.send(f'Python unit test, {func}, message {i+1}')

        expected = i + 1
        response_list = m.last_api_responses(n=expected)

        self.assertIsInstance(response_list, list)
        self.assertEqual(len(response_list), expected)


if __name__ == '__main__':
    unittest.main()
