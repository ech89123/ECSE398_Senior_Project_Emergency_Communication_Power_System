#import relevant libraries
from email_carc import Email_carc
from text_carc import Text_carc
from alert import Alert, Alert_Battery_Charged, Alert_Battery_Critical, Alert_Main_Power_Off, Alert_Main_Power_On

class Subroutine():
    #class represents a generic subroutine
    #functional subroutine A_B
    @staticmethod
    def subroutine_A_B():
        #run the actions for A to B
        #send the email - main power off when the battery is sufficiently charged
        Email_carc.send_email(Alert_Main_Power_Off())
        #send the text
        c = Text_carc()
        c.send_text(Alert_Main_Power_Off())
        print("Subroutine called..")
        #other state change actions
    
    #functional subroutine B_C
    @staticmethod
    def subroutine_B_C():
        #run the actions for B to C
        #send the email - critical battery depletion
        Email_carc.send_email(Alert_Battery_Critical())
        #send the text
        c = Text_carc()
        c.send_text(Alert_Battery_Critical())
        #other state change actions
    
    #functional subroutine C_D
    @staticmethod
    def subroutine_C_D():
        #run the actions for C to D
        #send the email - Main power restored and battery is critical
        Email_carc.send_email(Alert_Main_Power_On())
        #send the text
        c = Text_carc()
        c.send_text(Alert_Main_Power_On())
        #other state change actions
    
    #functional subroutine D_A
    @staticmethod
    def subroutine_D_A():
        #run the actions for D to A
        #send the email - Battery sufficiently charged
        Email_carc.send_email(Alert_Battery_Charged())
        #send the text
        c = Text_carc()
        c.send_text(Alert_Battery_Charged())
        #other state change actions

    #functional subroutine D_C
    @staticmethod
    def subroutine_D_C():
        #run the actions for D_C
        #This is the same as a main power off (A_B) except this time the battery is also critical
        Email_carc.send_email(Alert_Main_Power_Off())
        #send the text
        c = Text_carc()
        c.send_text(Alert_Main_Power_Off())
        #other state change actions

    #functional subroutine B_A
    @staticmethod
    def subroutine_B_A():
        #run the actions for B_A
        #This is the same as a main power on (A_B) except this time the battery is also sufficiently charged
        Email_carc.send_email(Alert_Main_Power_On())
        #send the text
        c = Text_carc()
        c.send_text(Alert_Main_Power_On())
        #other state change actions
