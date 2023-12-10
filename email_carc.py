#import the Deliverable class
from deliverable import Deliverable
import yagmail

#class definition of the email sending class
class Email_carc:
    
    #define a function
    @staticmethod
    def send_email(deliverable: Deliverable):
        #prepaing the attachments
        attachment_path = "/home/pi/Desktop/ProgramFiles/data.csv"
        #create an email client and authenticate
        yag_client = yagmail.SMTP(deliverable.FROM_ADDRESS, oauth2_file='CARC_Secret_Authentication_file.json')
        yag_client.login()
        #Prepare the attachments if provided
        attachments_ = [attachment_path]
        #send the email with the deliverable's information
        yag_client.send(
            to = deliverable.TO_ADDRESS, 
            subject = deliverable.email_subject, 
            contents = deliverable.email_message + '\n Sincerely, \n Case Amateur Radio Club.',
            attachments = attachments_
            )
        print("email sent")
