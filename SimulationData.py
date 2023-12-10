#import numpy as np
#import matplotlib.pyplot as plt
import time

class SimulationData:
    def __init__(self, length, batteryPowerIsOnSequence, depletionTime, chargeTime, batteryCapacity):
        #the length of time the simulated data runs for (seconds)
        self.length = length
        #is true when the battery power is on 
        self.batteryPowerIsOnSequence = batteryPowerIsOnSequence
        #is the time it takes for the battery to depelete (seconds)
        self.depletionTime = depletionTime
        #is the time it takes for the battery to charge (seconds)
        self.chargeTime = chargeTime

        self.batteryPercent = 100

        self.chargeCurrent = (batteryCapacity*3600)/chargeTime
        self.depletionCurrent = (batteryCapacity*3600)/depletionTime
        print(self.chargeCurrent)
        print(self.depletionCurrent)


        self.postPSUVoltageSensorArray = np.array([])
        self.batteryVoltageSensorArray = np.array([])
        self.currentSensorArray = np.array([])
        self.batteryPercentArray = np.array([])

        stateLength = self.getLength()/len(self.getBatteryPowerIsOnSequence())
        dataPointsPerState = stateLength
        self.buildPostPSUVoltageSensorData(dataPointsPerState)
        self.buildBatteryVoltageSensorData(dataPointsPerState)
        self.buildBatteryPercentageArray(dataPointsPerState)
        self.buildCurrentArray(dataPointsPerState)
        

    def getLength(self):
        return self.length
    def getBatteryPowerIsOnSequence(self):
        return self.batteryPowerIsOnSequence
    def getChargeTime(self):
        return self.chargeTime
    def getDepletionTime(self):
        return self.depletionTime
    def getChargeCurrent(self):
        return self.chargeCurrent
    def getDepletionCurrent(self):
        return self.depletionCurrent
    

    def getPostPSUVoltageSensorArray(self):
        return self.postPSUVoltageSensorArray
    def getBatteryVoltageSensorArray(self):
        return self.batteryVoltageSensorArray
    def getCurrentSensorArray(self):
        return self.currentSensorArray
    def getBatteryPercentArray(self):
        return self.batteryPercentArray
    
    def setPostPSUVoltageSensorArray(self, postPSUVoltageSensorArray):
        self.postPSUVoltageSensorArray = postPSUVoltageSensorArray
    def setBatteryVoltageSensorArray(self, batteryVoltageSensorArray):
        self.batteryVoltageSensorArray = batteryVoltageSensorArray
    def setCurrentSensorArray(self, currentSensorArray):
        self.currentSensorArray = currentSensorArray
    def setBatteryPercentArray(self, batteryPercentArray):
        self.batteryPercentArray = batteryPercentArray
    
    def getBatterPercent(self):
        return self.batteryPercent
    def setBatteryPercent(self, percent):
        self.batteryPercent = percent
    
    
    def buildPostPSUVoltageSensorData(self, dataPointsPerState):
        for char in self.getBatteryPowerIsOnSequence():
            if char == "F":
                self.setPostPSUVoltageSensorArray(np.append(self.getPostPSUVoltageSensorArray(), np.full(int(dataPointsPerState), 14))) 
            else: 
                self.setPostPSUVoltageSensorArray(np.append(self.getPostPSUVoltageSensorArray(), np.full(int(dataPointsPerState), 0))) 


    def buildBatteryVoltageSensorData(self, dataPointsPerState):
            batteryVoltageTracker = 13.6

            arrayOfBatteryVoltage = np.array([13.6, 13.4, 13.3, 13.2, 13.1, 13, 13, 12.9, 12.8, 12,10])
            arrayToReturn = np.array([])

            for char in self.getBatteryPowerIsOnSequence():
                if char == "T":
                    #creates depletion array given starting voltage
                    depletionArray = self.buildDepletionArray(arrayOfBatteryVoltage, batteryVoltageTracker)
                    #for the whole range of the state
                    for x in range(0, int(dataPointsPerState)):
                        #if the depletion array has not ran out then add the value from the depletion array
                        if x < len(depletionArray):    
                            arrayToReturn = np.append(arrayToReturn, [depletionArray[x]])
                            batteryVoltageTracker = depletionArray[x]
                        #if it has just add 10
                        else: 
                            arrayToReturn = np.append(arrayToReturn, [10]) 
                            batteryVoltageTracker = 10
                #here the voltage will increase as the PSU is on
                else:
                    #creates charge array given starting point 
                    chargeArray = self.buildChargeArray(arrayOfBatteryVoltage, batteryVoltageTracker)
                    for x in range(0, int(dataPointsPerState)):
                        #if the depletion array has not ran out then add the value from the depletion array
                        if x < len(chargeArray):    
                            arrayToReturn = np.append(arrayToReturn, [chargeArray[x]])
                            batteryVoltageTracker = chargeArray[x]
                        #if it has just add 10
                        else: 
                            arrayToReturn = np.append(arrayToReturn, [13.6]) 
                            batteryVoltageTracker = 13.6
            
            self.setBatteryVoltageSensorArray(arrayToReturn)

    def buildCurrentArray(self, dataPointsPerState):
        for char in self.getBatteryPowerIsOnSequence():
            if char == "F":
                for x in range(int(dataPointsPerState)):
                        if self.getBatteryPercentArray()[x] == 0:
                            self.setCurrentSensorArray(np.append(self.getCurrentSensorArray(), 0))
                        else:
                            self.setCurrentSensorArray(np.append(self.getCurrentSensorArray(), -1 * self.getChargeCurrent()))
            else:
                for x in range(int(dataPointsPerState)):
                        if self.getBatteryPercentArray()[x] == 0:
                            self.setCurrentSensorArray(np.append(self.getCurrentSensorArray(), 0))
                        else:
                            self.setCurrentSensorArray(np.append(self.getCurrentSensorArray(), self.getDepletionCurrent()))

    def buildBatteryPercentageArray(self, dataPointsPerState):
        for char in self.getBatteryPowerIsOnSequence():
            if char == "F":
                rateOfChange = 100/(self.getChargeTime())
                for x in range(int(dataPointsPerState)):
                        self.setBatteryPercent(min(self.getBatterPercent() + rateOfChange, 100))
                        self.setBatteryPercentArray(np.append(self.getBatteryPercentArray(), self.getBatterPercent()))
            else:
                rateOfChange = 100/(self.getDepletionTime())
                for x in range(int(dataPointsPerState)):
                        self.setBatteryPercent(max(self.getBatterPercent() - rateOfChange, 0))
                        self.setBatteryPercentArray(np.append(self.getBatteryPercentArray(), self.getBatterPercent()))
                

    def buildDepletionArray(self, arrayOfBatteryVoltage, batteryVoltageTracker):
        depletionArray = np.array([])
        for x in range(0,10):
            if arrayOfBatteryVoltage[x] >= batteryVoltageTracker >= arrayOfBatteryVoltage[x+1]:
                percentLeft = 1 - ((arrayOfBatteryVoltage[x] - batteryVoltageTracker)/(arrayOfBatteryVoltage[x] - arrayOfBatteryVoltage[x+1]))
                dataPointsLeft = percentLeft * self.getDepletionTime()/10
                depletionArray = np.append(depletionArray, self.givenBoundsCreateLinearArray(batteryVoltageTracker, arrayOfBatteryVoltage[x+1], dataPointsLeft))
                newStartPoint = arrayOfBatteryVoltage[x+1]
                break
        
        for x in range(0,10):
            if newStartPoint >= arrayOfBatteryVoltage[x]:
                 dataPointsPerStateTenPercent = self.getDepletionTime()/10
                 depletionArray = np.append(depletionArray, self.givenBoundsCreateLinearArray(arrayOfBatteryVoltage[x], arrayOfBatteryVoltage[x+1], dataPointsPerStateTenPercent))

        return depletionArray 
     

    def buildChargeArray(self, arrayOfBatteryVoltage, batteryVoltageTracker):
        chargeArray = np.array([])
        for x in range(0,10):
            
            if arrayOfBatteryVoltage[x] >= batteryVoltageTracker >= arrayOfBatteryVoltage[x+1]:
                percentLeft = ((arrayOfBatteryVoltage[x] - batteryVoltageTracker)/(arrayOfBatteryVoltage[x] - arrayOfBatteryVoltage[x+1]))
                dataPointsLeft = percentLeft * self.getChargeTime()/10 
                
                chargeArray = np.append(chargeArray, self.givenBoundsCreateLinearArray(batteryVoltageTracker,arrayOfBatteryVoltage[x], dataPointsLeft))
                newStartPoint = arrayOfBatteryVoltage[x]
                break

        for x in range(0,10):
            if newStartPoint <= arrayOfBatteryVoltage[10-x]:
                 dataPointsPerStateTenPercent = self.getChargeTime()/10
                 chargeArray = np.append(chargeArray, self.givenBoundsCreateLinearArray(arrayOfBatteryVoltage[10-x], arrayOfBatteryVoltage[9 - x],  dataPointsPerStateTenPercent))
                 
        return chargeArray 


        
    def givenBoundsCreateLinearArray(self, pointA, pointB, points):

        if points == 0:
            return np.array([])
        
        arrayToReturn = np.array([])
        delta = pointA-pointB
        for j in range(int(points)):
            voltage = pointA - (j*delta/points)
            arrayToReturn = np.append(arrayToReturn, [voltage])
        return arrayToReturn

    #def plotArrays(self):
        #lst1 = list(range(1,len(self.getPostPSUVoltageSensorArray())+1))
        #lst2 = list(range(1,len(self.getBatteryVoltageSensorArray())+1))
        #plt.subplot(2, 1, 1)
        #plt.plot(lst1, self.getPostPSUVoltageSensorArray(), label = "PSU", color = 'blue', linewidth = '3')
        #plt.plot(lst2, self.getBatteryVoltageSensorArray(), label = "Battery", color = 'black', linewidth = '3')
        #plt.title("Simulated Power Supply and Battery Voltages") 
        #plt.xlim([0, self.getLength()])
        #x = np.arange(0.0, self.getLength(), 0.1)
        #y1 = np.full(len(x), 12.8)
        #y2 = np.full(len(x), 13.6)
        #y3 = np.full(len(x), 10)
        #plt.fill_between(x, y1, y2, where = y1 <= y2, facecolor ='green', alpha = 0.6) 
        #plt.fill_between(x, y3, y1, where = y3 <= y1, facecolor ='orange', alpha = 0.6) 
        #plt.legend(['Power Supply Voltage', 'Battery Voltage', 'Battery Good (Above 20%)', 'Battery Low (Below 20%)'])
        #plt.xlabel("Samples")
        #plt.ylabel("Voltage (V)")
        #for x in range(0,self.getLength()): 
            #if alertArray[x] == 1:
                #plt.axvline(x, color = 'g', label = 'axvline - full height')

        #plt.subplot(2, 1, 2)
        #lst3 = list(range(1,len(self.getCurrentSensorArray())+1))
        #plt.plot(lst3, self.getCurrentSensorArray(), label = "PSU", color = 'black', linewidth = '3')
        #plt.axhline(y = self.getChargeCurrent() * -1, color = 'green', linestyle = 'dashed', linewidth = '2') 
        #plt.axhline(y = 0, color = 'black', linestyle = 'dashed', linewidth = '2') 
        #plt.axhline(y = self.getDepletionCurrent(), color = 'red', linestyle = 'dashed', linewidth = '2') 
        #plt.xlim([0, self.getLength()])
        #plt.legend(['Current', 'Depletion Current', 'Zero Current', 'Charging Current'])
        #plt.title("Simulated Current Output") 
        #plt.xlabel("Samples")
        #plt.ylabel("Current (A)")
        #for x in range(0,self.getLength()): 
            #if alertArray[x] == 1:
                #plt.axvline(x, color = 'g', label = 'axvline - full height')
        #plt.show()

#batterCapacity = 1
#length = 1000
#batteryPowerIsOnSequence = "FTFT"
#depletionTime = 36
#chargeTime = 36

#data = SimulationData(length, batteryPowerIsOnSequence, depletionTime, chargeTime, batterCapacity)
#data.plotArrays()
