from VoltageSensor import VoltageSensor
from CurrentSensor import CurrentSensor
from Battery import Battery
from SimulationData import SimulationData
from output import Output
#import numpy as np

import queue
import schedule
import csv
from datetime import datetime
import sched
import time

import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
import I2C_LCD_driver



class System:
    def __init__(self, batteryCapacity, batteryChargeCurrent, simulated, length, samplingRate, batteryPowerIsOnSequence, depletionTime, chargeTime, csvBuffer):

        #we assume to start that the batteries are charged and that the system is running on PSU power (State A)
        self.batteryCritical = False
        self.batteryPower = False
        self.state = "A"
        self.isSimulated = simulated

        #the sampling rate is the amount of seconds per sample
        self.samplingRate = samplingRate

        self.oldState = None
        self.alertFlag = False

        #we start by making simulated data nothing
        self.simulatedData = None 
        
        self.mylcd = I2C_LCD_driver.lcd()
        self.mylcd.lcd_clear()
        
        chan1 = None
        chan2 = None
        chan3 = None
        
        #if the data is simulated then we switch over to making the simulated data
        if simulated:
            self.simulatedData = SimulationData(length, batteryPowerIsOnSequence, depletionTime, chargeTime, batteryCapacity)
        else:
            GPIO.setmode(GPIO.BCM)
            # Create the I2C bus
            i2c = busio.I2C(board.SCL, board.SDA)

            # Create the ADC object using the I2C bus
            ads = ADS.ADS1015(address=0x48, i2c=i2c)

            # Create single-ended input on channel 0
            chan1 = AnalogIn(ads, ADS.P0)
            chan2 = AnalogIn(ads, ADS.P1)
            chan3 = AnalogIn(ads, ADS.P2)




        #csv buffer is the time (seconds) before the state change that is saved and sent via email
        self.dataPointsofCSV = round(csvBuffer/self.samplingRate,0)
        #on bootup clear the csv
        f = open("/home/pi/Desktop/ProgramFiles/data.csv", "w")
        f.truncate()
        f.close()

        #these are the two voltages and current vars
        self.batteryVoltage = 0
        self.batteryCurrent = 0
        self.psuVoltage = 0    

        #these are the queues to track filtering of data
        self.queueOfVoltagePSU = queue.Queue()
        self.queueOfBatteryVoltages = queue.Queue()
        self.queueOfBatteryCurrent = queue.Queue()

        #these are where the two voltage sensors, the current sensor, and the battery classes are made
        self.currentSensor = CurrentSensor(chan3, self.simulatedData)
        self.batteryVoltageSensor = VoltageSensor(chan1, self.simulatedData, 1)
        self.postPSUVoltageSensor = VoltageSensor(chan2, self.simulatedData, 2)
        self.battery = Battery(batteryCapacity, batteryChargeCurrent, samplingRate, self.isSimulated)
        
        self.state = self.checkForState()
		
        
    #-----------------------------------------
    #BELOW ARE THE SETTER AND GETTER METHODS
    #-----------------------------------------

    #here is the setter and getter for the batteryCritical var
    #batteryCritical should be false at init and changed to true when battery drops to 20%
    #batteryCritical should be changed back to false when batter comes back above 80%
    def getBatteryCritical(self):
        return self.batteryCritical
    def setBatteryCritical(self, batteryCritical):
        self.batteryCritical = batteryCritical

    #here is the setter and getter for the batteryPower var
    #batteryPower is init as false and is changed to true when the battery system is suplying power to the system
    #batteryPower is changed back to false when the batteries no longer power the system
    def getBatteryPower(self):
        return self.batteryPower
    def setBatteryPower(self, batteryCritical):
        self.batteryPower = batteryCritical
    
    #says if the system is running on simulated data
    def getIsSimulated(self):
        return self.isSimulated
    
    #here is the setter and getter for the currentState var
    #State A is when the system is powered by the grid and the battery power is good (system is running as normal)
    #State B is when the system is powered by the batteries and the power is good (emergency system is running)
    #State C is when the system is powered by the batteries and the power is critical (emergency system is running)
    #State D is when the system is powered by the grid and the battery power is low (batteries are charging)
    def getCurrentState(self):
        return self.state
    def setCurrentState(self, currentState):
        self.state = currentState

    #here is the setter and getter for the oldState var
    def getOldState(self):
        return self.oldState
    def setOldState(self, oldState):
        self.oldState = oldState

    # here is the getter and setter for the alert flag
    def getAlertFlag(self):
        return self.alertFlag
    def setAlertFlag(self, alertFlag):
        self.alertFlag = alertFlag

    #here is the getter for the sampling rate, this is the rate at which voltage, current, and state will be checked
    def getSamplingRate(self):
        return self.samplingRate

    #here is the getter setter for the current battery voltage
    def getBatteryVoltage(self):
        return self.batteryVoltage
    def setBatteryVoltage(self, voltage):
        self.batteryVoltage = voltage 

    #here is the getter setter for the current battery current
    def getBatteryCurrent(self):
        return self.batteryCurrent
    def setBatteryCurrent(self, current):
        self.batteryCurrent = current

    #here is the getter setter for the current PSU voltage
    def getPSUVoltage(self):
        return self.psuVoltage
    def setPSUVoltage(self, voltage):
        self.psuVoltage = voltage 

    def getDisplay(self):
        return self.mylcd 
        
    def getDataPointsofCSV(self):
        return self.dataPointsofCSV

    #here is the getter for the current sensor, two voltage sensors, and battery
    def getCurrentSensor (self):
        return self.currentSensor
    def getBatteryVoltageSensor(self):
        return self.batteryVoltageSensor
    def getPostPSUVoltageSensor(self):
        return self.postPSUVoltageSensor
    def getBattery(self):
        return self.battery
    
    #this is the getter for the simulated data made in the innit
    def getSimulatedData(self):
        return self.simulatedData
    
    #this gets the queue of PSU voltages for filtering
    def getQueueOfVoltagePSU(self):
        return self.queueOfVoltagePSU
    
    #this gets the queue of battery voltages for filtering
    def getQueueOfBatteryVoltages(self):
        return self.queueOfBatteryVoltages
    
    #this gets the queue of battery current for filtering
    def getQueueOfBatteryCurrent(self):
        return self.queueOfBatteryCurrent
    
    #-----------------------------------------
    #BELOW ARE THE METHODS TO CHECK STATE
    #-----------------------------------------

    #checks if the state has changed and updates them
    #this also triggers the alert flag which can be used to see if an alert needs to be sent
    def checkForNewState(self):
        tempState = self.checkForState()
        if tempState == self.getCurrentState():
            return False
        else:
            self.setOldState(self.getCurrentState())
            self.setCurrentState(tempState)
            self.setAlertFlag(True)
            return True
            

    #checks if the battery is critical and if the batteries are powering the system to determine the state
    def checkForState(self): 

        self.checkBatteryCritical()
        self.checkBatteryPowerIsOn()

        if self.getBatteryCritical() and self.getBatteryPower():
            return "C"
        elif ~self.getBatteryCritical() and self.getBatteryPower():
            return "B"
        elif self.getBatteryCritical() and ~self.getBatteryPower():
            return "D"
        else:
            return "A"
    
    #this method checks if the battery is powering the system
    def checkBatteryPowerIsOn(self):
        rawVoltage = self.getPostPSUVoltageSensor().getVoltage()
        if rawVoltage == None:
            return 
        
        voltage = self.cleanVoltageData(rawVoltage, self.getQueueOfVoltagePSU())
        self.setPSUVoltage(voltage)

        if voltage < 5:
            self.setBatteryPower(True)
        else:
            self.setBatteryPower(False)

    #checks and updates if the battery is critical 
    def checkBatteryCritical(self):
        #For current implementation, battery voltage is not used to see if the battery is critical
        #Although it is not used, the voltage is still read and updated as a global var so that it can be sent in the csv
        rawVoltage = self.batteryVoltageSensor.getVoltage()
        if rawVoltage == None:
            return 
        
        voltage = self.cleanVoltageData(rawVoltage, self.getQueueOfBatteryVoltages())
        self.setBatteryVoltage(voltage)

        if self.getBatteryCritical():
            if self.getBattery().getPercentage() >= 80:
                self.setBatteryCritical(False)
        else:
            if self.getBattery().getPercentage() <= 20:
                self.setBatteryCritical(True)

    
    #cleans the voltage data by multiplying it up to proper scale and filters it
    #this method is called anytime a voltage reading is called for
    def cleanVoltageData(self, rawVoltage, dataQueue: queue.Queue):
        multipliedVoltage = 37.5/7.5*rawVoltage
        return self.filterDataPoints(dataQueue, multipliedVoltage)
    
    #cleans the current data by multiplying it up to proper scale and filters it
    #this method is called anytime a voltage reading is called for
    def cleanCurrentData(self, rawCurrent, dataQueue: queue.Queue):
        multipliedCurrent = 50*rawCurrent
        return self.filterDataPoints(dataQueue, multipliedCurrent)
    
    #this is the method that actually filters for the above data points
    def filterDataPoints(self, dataQueue: queue.Queue, value):
        dataQueue.put(value)
        if dataQueue.qsize() > 10:
            dataQueue.get()
        return sum(list(dataQueue.queue)) / len(list(dataQueue.queue))

    #this method gets the current data and uses it to update the battery percentage
    def readAndInterpretCurrent(self): 
        rawCurrent = self.getCurrentSensor().getCurrent()
        if rawCurrent == None:
            return
        
        current = self.cleanCurrentData(rawCurrent, self.getQueueOfBatteryCurrent())
        if current < 0.4:
            self.getBattery().updateBatteryPercentage(self.getBatteryPower(), 0)
            self.getBattery().updateBatteryPercentage(self.getBatteryPower(), 0)
        else:
            current = (0.0829412*current) + 0.384118 + current + 0.5
            self.setBatteryCurrent(current)
            self.getBattery().updateBatteryPercentage(self.getBatteryPower(), current)
        print("Filtered Current: " + str(current))

    def sendAlert(self):
        if self.getIsSimulated() != True: 
            Output.launch(self.getOldState(), self.getCurrentState())
            #for testing
            print("")
            print("SENDING AN ALERT") 
            print("Old State: " + self.getOldState())
            print("New State: " + self.getCurrentState()) 
            print("")
    
    def updateDisplay(self): 
        self.getDisplay().lcd_clear()
        self.getDisplay().lcd_display_string("PSU Volt: " + str(round(self.getPSUVoltage(), 2)) + "V", 1)
        self.getDisplay().lcd_display_string("Bat Volt: " + str(round(self.getBatteryVoltage(), 2)) + "V", 2)
        self.getDisplay().lcd_display_string("Bat Pct: " + str(round(self.getBattery().getPercentage(), 1)), 3)
        self.mylcd.lcd_display_string("Current State: " + self.getCurrentState(), 4)
    
        

    #-----------------------------------------
    #BELOW ARE THE CSV Methods
    #-----------------------------------------

    def clearCSV():
        f = open("/home/pi/Desktop/ProgramFiles/data.csv", "w")
        f.truncate()
        f.close()

    def innitCSV(self): 
        field_names = ['Time', 'PSU Voltage', 'Bat Voltage',
               'Bat Current', 'Batt Percentage', 'State']
        with open('/home/pi/Desktop/ProgramFiles/data.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(field_names)

    def writeLineToCSV(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        dataToAdd = [current_time, round(self.getPSUVoltage(),3) , round(self.getBatteryVoltage(),3), 
                     round(self.getBatteryCurrent(),3), round(self.getBattery().getPercentage(),3), self.getCurrentState()]
        with open('/home/pi/Desktop/ProgramFiles/data.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(dataToAdd)
        
    def removeTop(self):
            field_names = ['Time', 'PSU Voltage', 'Bat Voltage',
               'Bat Current', 'Batt Percentage', 'State']
            #read the csv
            with open('/home/pi/Desktop/ProgramFiles/data.csv', 'r', newline='') as csvfile:
                csv_reader = csv.reader(csvfile)
                next(csv_reader, None)
                next(csv_reader, None)
                data = [row for row in csv_reader]

            #rewrite the csv
            with open('/home/pi/Desktop/ProgramFiles/data.csv', 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(field_names)
                csv_writer.writerows(data)


    def getRowCount(self):
        with open('/home/pi/Desktop/ProgramFiles/data.csv', 'r', newline='') as csvfile:

            csv_reader = csv.reader(csvfile)
            row_count = sum(1 for row in csv_reader)
        return row_count

    def mainCSVMethod(self):
        self.writeLineToCSV()
        if self.getRowCount() > (self.getDataPointsofCSV()):
            self.removeTop()

    #-----------------------------------------
    #BELOW IS THE MAIN LOOP FROM WHICH THE PROGRAM RUNS
    #-----------------------------------------

    def mainLoop (self):
        #this checks the current and interprets it
        self.readAndInterpretCurrent()
        #this checks for a new state and updates it accordingly
        self.checkForNewState()
        #this checks if there was a state change and if there was then send an alert
        if self.getAlertFlag():
            self.sendAlert()
            self.setAlertFlag(False)
        #this updates the display based on the new values
        self.updateDisplay()
        #this updates the csv file with current metrics
        self.mainCSVMethod()
        print("Another Loop")

    def simulatedDataLoop(self):
        print("to be implemented later")
        #aletFlagArray = np.zeros(self.getSimulatedData().getLength())
        #for x in range(0,self.getSimulatedData().getLength()):
            #self.checkForNewState()
            #self.readAndInterpretCurrent()
            #print(self.getBattery().getPercentage())
            #if self.getAlertFlag():
                #aletFlagArray[x] = 1
                #self.setAlertFlag(False)
        #self.getSimulatedData().plotArrays()

def main():
    print("in main")
    #system = System(1, 5, True, 1000, 1, "FTFT", 36, 36, 10)
    system = System(0.05, 10, False, 1000, 2, "FTFT", 36, 36, 15)
    system.innitCSV()
    if system.getIsSimulated():
        system.simulatedDataLoop()
    else:
        schedule.every(system.getSamplingRate()-0.25).seconds.do(system.mainLoop) 
        while True: 
            schedule.run_pending()
    
if __name__=="__main__":
    main()
