# Simple Message

Simple Message is a Python 3 package that simplifies the task of sending basic Slack messages. In as few as the following lines of code, you can send Slack messages to a channel. Any additional messages can be sent with just one simple line of code. It handles logging and error handling, and makes available a full history of responses to API calls made within a session.

```python
import simple_message as sm

m = sm.SimpleMessage("YOUR API TOKEN", destination_id="YOUR CHANNEL ID")
m.send('Hello world!')

```
In a typical use case, you might have a batch job and would like to be notified when the job starts or stops, or if it encounters some condition, checkpoint milestone, or exception. It is not intended for two-way communication or complex messaging that Slack offers.

A key design objective of this utility is to provide minimize the boilerplate needed to send a basic message. This makes the code flexible in a way that switching in the future to an alternate service such as Twilio for notifications could minimize the effort required to refactor every program that otherwise directly embeds the native Slack SDK commands. See the example in their [API docs](https://slack.dev/python-slack-sdk/web/index.html#messaging). Their example shows how the post method would normally be wrapped in a try/except block. This package will handle those exceptions for you and will return a boolean to indicate success, without halting execution of your primary code, while providing methods for troubleshooting the stored API responses directly.

As of now, only the Slack service is supported. I believe that a paid account is not required to use the messaging service. Internally, this program is wrapping Slack WebClient [chat_postMessage()](https://slack.dev/python-slack-sdk/web/index.html#messaging) messaging code.

## Installation
Install the package using pip (conda install is not available at this time). The Slack SDK package is the only package dependency will be installed if not detected in your environment.
```python
pip install simple_message
```

## Slack Configuration

These are the recommended steps to get your Slack credentials set up. You need to create an "app" with appropriate permissions, a Slack API token, and a channel id to send messages. If you have existing tokens or channels you'd like to use, then skip to an appropriate step below.
1. Go to https://api.slack.com/apps and click the [Create New App] button.
   1. Choose [From Scratch].
   2. Choose a name for your app. It can be changed later on the Slack API page under Features/App Home/Your App's Presence in Slack.
   3. Select from the dropdown menu to pick a workspace for your app. If you don't have a workspace, log into Slack and create one first.
   4. Upon completion of the last step, scroll down the page to the Building Apps for Slack section and click [Install your app], then click [permission scope].
   5. Under the Scopes section, Bot Token Scopes subsection, click [Add an OAuth Scope], and select the chat:write scope. A "Success" flash notification should appear at the top of the page after the selection.
   6. Again, in the Scopes section, click [Add an OAuth Scope], and select the 'channels:join' scope. If requested to reinstall your app, click the hyperlink and click [Allow]. This gives it permission to perform actions in channels and conversations.
   7. On the same page, OAuth & Permissions, look at the OAuth Tokens for Your Workspace section and click [Install to Workspace]. This option was not available before you added the scopes in the previous steps.
   8. You will see a page requesting permission for the app to access the workspace. Click [Allow].
   9. Now you can look in your Slack desktop app and see the app you created under the Apps section in the left frame.
   10. Back on the Slack API webpage, under the OAuth Tokens for your Workspace section, you will see a long token like xxxx-12345678912-12345678912-xxxxxxxxxxxxxxxxxxx with a [Copy] button to the right. Copy it to your clipboard.
2. Create an environment variable with any name and assign your copied OAuth token to it. Alternately, you could hard code the token into your own code every time you need it, though for obvious reasons this is not recommended. (How to set environment variables in [Windows](https://itsiti.com/how-to-set-environment-variables-in-windows-server/) using sysdm.cpl and in [OS X](https://phoenixnap.com/kb/set-environment-variable-mac))
3. Go to your Slack desktop app and select the workspace. Right-click on the channel that should receive messages (or create a test channel first and then right-click it). Select 'Open channel details'.
4. At the very bottom of the dialog box you will see a Channel ID. Copy it to the clipboard.
5. Create another environment variable with any name and assign the channel id to it.
6. Next, create another environment variable named "SIMPLE_MESSAGE_TYPE_DEFAULT" and assign the value "slack" (case-insensitive) to it. The program searches for this _specific_ environment variable to determine the service to use as a default. By using this name you will not need to explicitly specify using Slack as the service type. In the future should your needs change and you must switch to a different messaging service, you will not need to update your code to change the service selection if you rely on this environment variable. Instead you would update the value of the environment variable once the new service has been implemented. However, you are free to use any name, in which case you will need to pass it to the parameter "msg_service_env_name" during instantiation.
7. Before any channel can receive messages from your app, in the desktop app you need to right-click the app and select 'Open app details'.
8. Then click the 'Add this app to a channel' button and select the intended channel. To validate that the app was successfully added to the channel, right-click the channel and again select 'Open channel details', then go to the Integrations tab and you should see your app name under the Apps section.
9. On the Slack API page you can review your app settings under Settings/App Manifest in both YAML and JSON formats (currently a beta feature). Otherwise, you can navigate through sections under Settings/Basic Information. You can verify that your app has the chat:write and channels:join scopes in your yaml file, which should resemble the following:

```yaml
_metadata:
  major_version: 1
  minor_version: 1
display_information:
  name: NotificationDemoApp
features:
  bot_user:
    display_name: NotificationDemoApp
    always_online: false
oauth_config:
  scopes:
    bot:
      - chat:write
      - channels:join
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```

## Usage

After the above steps are complete, you are ready to test. With the environment variables in place, a typical basic setup might look like this:

```python
import simple_message as sm
import os

msg_token = os.environ.get('SIMPLE_MESSAGE_API_TOKEN')
channel_id = os.environ.get('SLACK_CHANNEL_ID_DEMO')

m = sm.SimpleMessage(token=msg_token, destination_id=channel_id)
m.send('Hello world!')  # send() returns True or False, indicating delivery success
```

In the above configuration, the message is directed to the channel configured during instantiation, so any additional messages will also be directed to the same channel by default.
### Multiple Channels
Should you need to send messages to different channels at various points in your code, you can do so by setting the destination_id parameter to the desired Slack channel ID in the send() call. Setting an id in this manner will override the destination_id set at the instance level. There is no ceiling on the number of channels you can use.

```python
channel_id2 = os.environ.get('SLACK_CHANNEL_ID_DEMO2')  # Adding a second channel
m.send('Hello world!', destination_id=channel_id2)
```

### Logging
By default, the python logging facility will log messages that meet the specified log level threshold. Should you instead prefer to capture these attempts to a log file, you can specify a log name. The default logging level is "WARNING", but can be changed to a valid logging level using the class parameter "logging_level". 

Valid logging levels are: DEBUG, INFO, WARNING, ERROR, CRITICAL, NOTSET. See the Python [logging docs](https://docs.python.org/3/howto/logging.html#basic-logging-tutorial) for more details.

NOTE: For convenience, an extension of .log will be appended to any log filename entered if you don't specify .log as the extension.
```python
log_filename = 'messages.log'

# Let's create a new instance and update its logging level to DEBUG, The argument's implementation here is case-insensitive and it should be passed as a str
m2 = sm.SimpleMessage(token=msg_token, destination_id=channel_id, log_filename=log_filename, logging_level='DEBUG')
```

## Troubleshooting
A Simple Message instance will store a list of all SlackResponse objects returned from each Slack API call.
```python
# e.g., setting n=4 will return the last 4 responses in a list
m.last_api_responses(n=4)

# Use this method to get the most recent response (singular, does not return a list)
m.last_api_response()  

# which is equivalent to the following:
response_list = m.last_api_responses(n=1)
response_list[0]  # SlackResponse instance
```
```python
<slack_sdk.web.slack_response.SlackResponse object at 0x7fbb002c5910>
```
Slack response attributes:
```python
# You can explore the available attributes of this object using dir()
dir(response_list[0])
```

```python  
['__class__',
 '__contains__',
 '__delattr__',
 '__dict__',
 '__dir__',
 '__doc__',
 '__eq__',
 '__format__',
 '__ge__',
 '__getattribute__',
 '__getitem__',
 '__gt__',
 '__hash__',
 '__init__',
 '__init_subclass__',
 '__iter__',
 '__le__',
 '__lt__',
 '__module__',
 '__ne__',
 '__new__',
 '__next__',
 '__reduce__',
 '__reduce_ex__',
 '__repr__',
 '__setattr__',
 '__sizeof__',
 '__str__',
 '__subclasshook__',
 '__weakref__',
 '_client',
 '_initial_data',
 '_iteration',
 '_logger',
 'api_url',
 'data',
 'get',
 'headers',
 'http_verb',
 'req_args',
 'status_code',
 'validate']
```
```python
# Or you can use __dict__ to inspect a fully populated dict of key/value pairs
response_list[0].__dict__  # Output not displayed here

# For example, the data attribute of SlackResponse shows the following:
from pprint import pprint
pprint(response_list[0].data)
```
```python
{'channel': 'xyz',
 'message': {'bot_id': 'xyz',
             'bot_profile': {'app_id': 'xyz',
                             'deleted': False,
                             'icons': {'image_36': 'https://a.slack-edge.com/80588/img/plugins/app/bot_36.png',
                                       'image_48': 'https://a.slack-edge.com/80588/img/plugins/app/bot_48.png',
                                       'image_72': 'https://a.slack-edge.com/80588/img/plugins/app/service_72.png'},
                             'id': 'xyz',
                             'name': 'workspace name',
                             'team_id': 'xyz',
                             'updated': 1630014102},
             'team': 'xyz',
             'text': 'Hello world',
             'ts': '1630385147.000900',
             'type': 'message',
             'user': 'xyz'},
 'ok': True,
 'ts': '1630385147.000900'}
```

Checking the HTTP status code:
```python
response_list[0].status_code
```
```python
200
```