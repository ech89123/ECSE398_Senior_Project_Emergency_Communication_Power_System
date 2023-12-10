#import numpy as np

class Battery:
    def __init__(self, capacity, maxChargeCurrent, samplingRate, isSimulated):
        self.capacity = capacity
        self.maxChargeCurrent = maxChargeCurrent 
        self.samplingRate = samplingRate
        self.percentage = 100
        self.isSimulated = isSimulated

    
    def getCapacity(self):
        return self.capacity
    
    def getMaxChargeCurrent(self):
        return self.maxChargeCurrent
    
    def getSamplingRate(self):
        return self.samplingRate
    
    def getPercentage(self):
        return self.percentage
    
    def setPercentage(self, percentage):
        self.percentage = percentage

    def getIsSimulated(self):
         return self.isSimulated
        


    def updateBatteryPercentage(self, dissipating, current):
        #current capacity of battery in Ah
        currentCapacity = (self.getCapacity() * self.getPercentage()/100)
        if (dissipating):
            #Here we know the battery is dissipating
            #capacity change in Ah
            changeInCapacity = ((current * self.getSamplingRate())/ 3600)
            #new battery percentage is through subtraction
            newCapacity = currentCapacity - changeInCapacity
            #if the new capactity is less than 0 then keep it at 0
            newCapacity = max((newCapacity)/self.getCapacity() * 100, 0)
            #new battery percentage
            self.setPercentage(newCapacity)
        else:
            #Here we know the battery is charging
            changeInCapacity = 0
            if self.getIsSimulated():
                changeInCapacity = ((current * self.getSamplingRate())/ 3600)
            else:
                changeInCapacity = ((self.getMaxChargeCurrent() * self.getSamplingRate())/ 3600)
            #new battery percentage is through addition
            newCapacity = currentCapacity + changeInCapacity
            #if the new capactity is greater than 100 then keep it at 100
            newCapacity = min((newCapacity)/self.getCapacity() * 100, 100)
            #new battery percentage
            self.setPercentage(newCapacity)
