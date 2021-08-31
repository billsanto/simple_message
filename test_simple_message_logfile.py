import unittest
import os
import simple_message as msg
import sys


class SimpleMessageTestLogfileCase(unittest.TestCase):
    msg_token = os.environ.get('SLACK_BOT_TOKEN')
    channel_id = os.environ.get('SLACK_CHANNEL_ID_DEMO')
    channel_id2 = os.environ.get('SLACK_CHANNEL_ID_DEMO2')

    def test_message_with_no_channel_id_check_logfile(self):
        """
            NOTE: This test needs to be run separately from the other unit tests to pass for an unknown reason

            Delete existing test logfile
            Send message with no destination_id
            Read log contents
            Check return value
            Check if message text is contained in log file contents
        """
        func = sys._getframe().f_code.co_name
        log_filename = 'test_message.log'

        if os.path.exists(log_filename):
            os.remove(log_filename)

        m = msg.SimpleMessage(token=self.msg_token, log_filename=log_filename)
        msg_text = f'Python unit test, {func}'
        rv = m.send(msg_text)

        if os.path.exists(log_filename):
            try:
                with open(log_filename, 'r') as f:
                    log_contents = f.read()
            except Exception as e:
                self.assertTrue(False, f'Could not open the logfile {log_filename}')
        else:
            self.assertTrue(False, f'Could not find the logfile {log_filename}')

        self.assertFalse(rv)
        self.assertIn(msg_text, log_contents)


if __name__ == '__main__':
    unittest.main()
