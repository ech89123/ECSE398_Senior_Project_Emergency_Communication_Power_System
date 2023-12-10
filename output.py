from subroutine import Subroutine
import sys

class Output:
    #The launch function calls a different subroutine for the specified arguments given 
    #defines the central launch function that launches a subroutine
    @staticmethod
    def launch(old_state : str, new_state : str):
        #checking inputs and calling the corresponding subroutine
        if (old_state == "a" or old_state == "A") and (new_state == "b" or new_state == "B"):
            #call the corresponding subroutine
            Subroutine.subroutine_A_B()
        
        if (old_state == "b" or old_state == "B") and (new_state == "a" or new_state == "A"):
            #call the corresponding subroutine
            Subroutine.subroutine_B_A()
        
        if (old_state == "c" or old_state == "C") and (new_state == "d" or new_state == "D"):
            #call the corresponding subroutine
            Subroutine.subroutine_C_D()
        
        if (old_state == "d" or old_state == "D") and (new_state == "c" or new_state == "C"):
            #call the corresponding subroutine
            Subroutine.subroutine_D_C()
        
        if (old_state == "b" or old_state == "B") and (new_state == "c" or new_state == "C"):
            #call the corresponding subroutine
            Subroutine.subroutine_B_C()
        
        if (old_state == "d" or old_state == "D") and (new_state == "a" or new_state == "A"):
            #call the corresponding subroutine
            Subroutine.subroutine_D_A()
            
def main(args):
    print("hello from the main function")
    Output.launch("a","b")

if __name__ == "__main__":
    main(sys.argv)
