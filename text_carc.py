#import the Deliverable class
from deliverable import Deliverable
from twilio.rest import Client

class Text_carc:
    # Twilio credentials
    account_sid = <add sid>
    auth_token = <add token>

    def send_text(self, deliverable : Deliverable):
        # Text configuration
        sender_number = deliverable.FROM_NUMBER
        receiver_number = deliverable.TO_NUMBER
        message = deliverable.email_message + '\n Sincerely, \n Case Amateur Radio Club.'
        client = Client(self.account_sid, self.auth_token)
        message = client.messages.create(
            body=message,
            from_=sender_number,
            to=receiver_number
        )
        print(f'Message sent with SID: {message.sid}')
