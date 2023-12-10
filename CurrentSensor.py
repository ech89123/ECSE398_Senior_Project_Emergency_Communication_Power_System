from SimulationData import SimulationData
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO

class CurrentSensor:
    def __init__(self, chan: AnalogIn, simulatedData: SimulationData):
        
        if simulatedData == None:
            self.isSimulated = False
        else:
            self.isSimulated = True

        self.simulatedData = simulatedData
        self.chan = chan
        self.dataCounter = -1

    def getIsSimulated(self):
        return self.isSimulated
    
    def getChannelObject(self):
        return self.chan
    
    def getDataCounter(self):
        return self.dataCounter
    
    def setDataCounter(self, dataCounter):
        self.dataCounter = dataCounter

    def getLength(self):
        return self.getSimulatedData().getLength()
    
    def getSimulatedData(self):
        return self.simulatedData
    
    def getCurrent(self):
        if self.getIsSimulated():
            if self.getLength() >= self.getDataCounter():
                self.setDataCounter(self.getDataCounter()+1)
                return self.getSimulatedData().getCurrentSensorArray()[self.getDataCounter()]
        else: 
            #getting data from I2C
            return self.getChannelObject().voltage
