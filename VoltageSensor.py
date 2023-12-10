from SimulationData import SimulationData
import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO

class VoltageSensor:
    def __init__(self, chan: AnalogIn, simulatedData: SimulationData, channelInt):
        
        if simulatedData == None:
            self.isSimulated = False
        else:
            self.isSimulated = True

        self.simulatedData = simulatedData

        self.dataCounter = -1

        self.chan = chan
        self.channelInt = channelInt


    def getIsSimulated(self):
        return self.isSimulated
    
    def getChannelObject(self):
        return self.chan
    
    def getSimulatedData(self):
        return self.simulatedData
    
    def getDataCounter(self):
        return self.dataCounter
    
    def setDataCounter(self, dataCounter):
        self.dataCounter = dataCounter
    
    def getLength(self):
        return self.getSimulatedData().getLength()
    
    def getChannelInt(self):
        return self.channelInt
    
    
    def getVoltage(self):
        if self.getIsSimulated():
            if self.getLength() >= self.getDataCounter():
                if self.getChannelInt() == 2:
                    #here we say it is the PSU voltage
                    self.setDataCounter(self.getDataCounter()+1)
                    return self.getSimulatedData().getPostPSUVoltageSensorArray()[self.getDataCounter() - 1]
                if self.getChannelInt() == 1:
                    #here we say it is the battery voltage
                    self.setDataCounter(self.getDataCounter()+1)
                    return self.getSimulatedData().getBatteryVoltageSensorArray()[self.getDataCounter() - 1]
        else: 
            return self.getChannelObject().voltage
