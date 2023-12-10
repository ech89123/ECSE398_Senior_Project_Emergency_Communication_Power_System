#import the abstract class module
from abc import ABC,abstractmethod
from deliverable import Deliverable

#class definition of a generic abstract Alert
class Alert(Deliverable, ABC):

    #methods to return the title and message defined in The Deliverable
    def get_title(self):
        return self.email_subject
    def get_message(self):
        return self.email_message 

#Subclasses inheriting from abstract class Alert
#Alert A_B (Main Power Off)
class Alert_Main_Power_Off(Alert):
    #instantiate the variables
    def __init__(self):
        super().__init__("[CARC] - MAIN POWER OFF","The main power has been turned off and the system is currently running on battery power.")

#Alert B_A and C_D (Main Power Restored)
class Alert_Main_Power_On(Alert):
    #instantiate the variables
    def __init__(self):
        super().__init__("[CARC] - MAIN POWER RESTORED","The main power has been restored. The system is currently running on main.")

#Alert B_C (Critical Battery Depletion)
class Alert_Battery_Critical(Alert):
    #instantiate the variables
    def __init__(self):
        super().__init__("[CARC] - BATTERY AT CRITICAL LEVEL","The battery has depleted below 20%! Restore main power or prepare for shutdown.")

#Alert D_A (Battery Sufficiently Charged)
class Alert_Battery_Charged(Alert):
    #instantiate the variables
    def __init__(self):
        super().__init__("[CARC] - BATTERY SUFFICIENTLY CHARGED","The battery has been sufficiently charged.")
