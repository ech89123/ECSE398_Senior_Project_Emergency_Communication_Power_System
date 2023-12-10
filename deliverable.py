#import abstract class functionality
from abc import ABC,abstractmethod

#Defines a class Deliverable which is sent by the email class
#Any class inheriting from Deliverable can be sent as an email
class Deliverable(ABC):

    #variables for the email
    TO_ADDRESS = "w8edu-emergency-communications@case.edu"
    TO_NUMBER = "2162355191"
    FROM_ADDRESS = "w8edu.comms@gmail.com"
    FROM_NUMBER = "8778130036"
    email_subject = ""
    email_message = ""

    #constructor to initialize the subject and email whenever a Deliverable is created
    def __init__(self, subject: str, message: str):
        self.email_subject = subject
        self.email_message = message

    #abstract methods to get the title and message
    @abstractmethod
    def get_title(self):
        pass
    @abstractmethod
    def get_message(self):
        pass
