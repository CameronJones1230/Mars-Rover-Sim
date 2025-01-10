import time
import random
from random import Random

import pygame
import settings
import queue
class Scheduler(pygame.sprite.Sprite):
    def __init__(self,player,RMS,WP,WC,IBP,IBC,COMP,COMCOMP,RP,RC,WPow,IBPow,COMPPOW,RPOW,battery,recharge,priorityInheritance,priorityCeiling):
        super().__init__()
        self.font = pygame.font.Font('freesansbold.ttf', 22)
        self.CurrentTask = self.font.render('GeeksForGeeks', True, (0,255,0), (0,0,255))
        self.CurrentTaskRect = self.CurrentTask.get_rect()
        self.CurrentTaskRect.center = (0,550)
        self.ready = PriorityQueue()
        self.ReadyText = self.font.render(str(self.ready), True, (0, 255, 0), (0, 0, 255))
        self.ReadyTextRect = self.CurrentTask.get_rect()
        self.ReadyTextRect.center = (0, 580)
        self.waiting = []
        self.terminated = PriorityQueue()


        self.TerminatedText = self.font.render(str(self.terminated), True, (0, 255, 0), (0, 0, 255))
        self.TerminatedRect = self.TerminatedText.get_rect()
        self.TerminatedRect.center = (0, 610)
        self.StartText = self.font.render('START', True, (0, 255, 0), (0, 0, 255))
        self.StartTextRect = self.StartText.get_rect()
        self.StartTextRect.center = (160,640)
        self.EndText = self.font.render('END', True, (0, 255, 0), (0, 0, 255))
        self.EndTextRect = self.StartText.get_rect()
        self.EndTextRect.center = (470, 640)
        self.CompText = self.font.render('END', True, (0, 255, 0), (0, 0, 255))
        self.CompTextRect = self.StartText.get_rect()
        self.CompTextRect.center = (470, 670)
        self.WeatherText = self.font.render("Current Temperature on Mars: " + "10" + "°C", True, (0, 255, 0), (0, 0, 255))
        self.WeatherTextRect = self.StartText.get_rect()
        self.WeatherTextRect.center = (950, 500)
        self.VMAText = self.font.render('VMA Bus', True, (0, 255, 0), (0, 0, 255))
        self.VMATextRect = self.StartText.get_rect()
        self.VMATextRect.center = (1020, 90)
        self.BusText = self.font.render('1553 Bus', True, (0, 255, 0), (0, 0, 255))
        self.BusTextRect = self.StartText.get_rect()
        self.BusTextRect.center = (1095,190)
        self.VMAHeldText = self.font.render('Open', True, (0, 255, 0), (0, 0, 255))
        self.VMAHeldTextRect = self.VMAHeldText.get_rect()
        self.VMAHeldTextRect.center = (1010, 115)
        self.BusHeldText = self.font.render('Open', True, (0, 255, 0), (0, 0, 255))
        self.BusHeldTextRect = self.BusHeldText.get_rect()
        self.BusHeldTextRect.center = (1100, 215)

        self.PowerText = self.font.render('10kW', True, (0, 255, 0), (0, 0, 255))
        self.PowerTextRect = self.PowerText.get_rect()
        self.PowerTextRect.center = (950, 600)

        self.TotalPowerText = self.font.render('10kW', True, (0, 255, 0), (0, 0, 255))
        self.TotalPowerTextRect = self.TotalPowerText.get_rect()
        self.TotalPowerTextRect.center = (950, 550)



        self.running = 0 # no tasks running
        self.Weather = WeatherThread(WP,WC,WPow)
        self.Bus = infoBusThread(IBP,IBC,IBPow)
        self.Com = CommunicationThread(COMP,COMCOMP,COMPPOW)
        self.rotor = rotorControl(RP,RC,RPOW)
        self.VMAbus = register()
        self.Bus1553 = register() #1553 bus
        self.Completion = 0
        self.CompPercent = 0 # the percent completion of the current task
        self.allTasks = [self.Weather,self.Bus,self.Com,self.rotor]
        self.curTask = self.Weather
        self.noTask = 0
        self.temp = 0
        self.taskStart = 0
        self.player = player
        self.DeadlinesMissed = 0

        self.priorityInheritance = priorityInheritance
        self.prioricyCeiling = priorityCeiling
        self.highestPriorityCeiling = 0
        self.RMS = RMS

        self.battery = battery
        self.batteryCharge = battery
        self.recharge = recharge
        self.start = time.time()
        self.RechargeText = self.font.render("recharge rate:" + str(self.recharge), True, (0, 255, 0), (0, 0, 255))
        self.RechargeTextRect = self.PowerText.get_rect()
        self.RechargeTextRect.center = (900, 650)
        self.PowerUseText = self.font.render("Power Use rate:" + str(self.recharge), True, (0, 255, 0), (0, 0, 255))
        self.PowerUseTextRect = self.PowerText.get_rect()
        self.PowerUseTextRect.center = (1100, 650)
        self.NoPowerTime = 0
        self.NoPowerStart = 0
        self.noPowerStarted = 0
        self.sunChangeTime = random.randint(1,10)
        self.SunStart = time.time()
        self.RRStart = 0
        self.RRstart = time.time()
        self.RRtime = 5
        self.deadLock = 0
        self.RRNowStarting = 1
        self.RRTaskList = [self.rotor,self.Bus,self.Com,self.Weather]
        self.RoundRobinText = self.font.render('Time', True, (0, 255, 0), (0, 0, 255))
        self.RoundRobinTextRect = self.BusHeldText.get_rect()
        self.RoundRobinTextRect.center = (200, 650)

    def RoundRobin(self):
        # if(self.RRNowStarting == 1):
        #     self.ready.insert(self.rotor)
        #     self.ready.insert(self.Bus)
        #     self.ready.insert(self.Com)
        #     self.ready.insert(self.Weather)
        #     self.RRNowStarting = 0
        self.ReadyText = self.font.render("READY:" + str(self.ready), True, (0, 255, 0), (0, 0, 255))
        self.CurrentTask = self.font.render(str(self.curTask), True, (0, 255, 0), (0, 0, 255))
        self.TerminatedText = self.font.render("TERM:" + str(self.terminated), True, (0, 255, 0), (0, 0, 255))
        self.PowerText = self.font.render(str(self.batteryCharge), True, (0, 255, 0), (0, 0, 255))
        self.RechargeText = self.font.render("recharge rate:" + str(self.recharge), True, (0, 255, 0), (0, 0, 255))
        self.RoundRobinText = self.font.render("round time allotted" + "{:.1f}".format((time.time() - self.RRStart)), True, (0, 255, 0), (0, 0, 255))
        if (self.running == 1 and self.curTask != None):
            self.PowerUseText = self.font.render("Power Use rate:" + str(self.curTask.PowerConsumption), True,
                                                 (0, 255, 0), (0, 0, 255))
        if (time.time() - self.SunStart >= self.sunChangeTime):
            self.recharge = random.randint(1, 1000)
            self.SunStart = time.time()
            self.sunChangeTime - random.randint(1, 10)

        #get new Task
        if(self.running == 0 and len(self.ready.queue) != 0):
            self.curTask = self.RRTaskList[0]
            self.RRStart = time.time()
            self.running = 1

        #print(time.time() - self.curTask.StartTime)
        if(time.time() - self.RRStart >= self.RRtime):
            self.running = 0
            self.RRTaskList[0] = self.RRTaskList[1]
            self.RRTaskList[1] = self.RRTaskList[2]
            self.RRTaskList[2] = self.RRTaskList[3]
            self.RRTaskList[3] = self.curTask




            self.RRStart += self.RRtime
            print(self.RRTaskList)

        #print(self.curTask.RRFinished)
        if(time.time() - self.RRStart >= self.curTask.compTime and self.curTask.RRFinished != 1):
            self.curTask.task(self.player, self.VMAbus, self.Bus1553, self)
            self.curTask.finish(self.Bus1553, self.VMAbus)
            self.curTask.RRFinished = 1
            self.terminated.insert(self.curTask)
            print("Finished")
            count = 0
            for x in self.ready.queue:
                if(x == self.curTask):
                    del self.ready.queue[count]
                count += 1

        else:
            self.CompPercent = (
                    ((time.time() - self.RRStart) - self.NoPowerTime) / (self.curTask.compTime))
            self.CompPercent = round(self.CompPercent, 2)
            # print(time.time() - self.curTask.StartTime)
            # print((self.curTask.compTime + self.NoPowerTime))
            if (self.CompPercent < 1):
                self.Completion = 200 * self.CompPercent
            self.CompPercent = 100 * self.CompPercent
            if (self.CompPercent >= 100):
                self.CompPercent = 100
            self.CompText = self.font.render("{:.1f}".format(self.CompPercent), True, (0, 255, 0), (0, 0, 255))

            # checks if any finished tasks are ready to return to the ready queue
        for x in self.terminated.queue:
            if (time.time() - x.StartTime) >= x.period:
                x.StartTime += x.period
                x.RRFinished = 0
                self.ready.insert(x)
                self.terminated.queue.remove(x)

        for x in self.ready.queue:
            if (time.time() - x.StartTime) >= x.period:
                x.StartTime += x.period
                self.DeadlinesMissed += 1
                print("missed deadline")





    def schedule(self):
            self.ReadyText = self.font.render("READY:" + str(self.ready), True, (0, 255, 0), (0, 0, 255))
            if(self.deadLock == 1):
                self.CurrentTask = self.font.render("NONE", True, (0, 255, 0), (0, 0, 255))
            else:
                self.CurrentTask = self.font.render("Current Task: " + str(self.curTask), True, (0, 255, 0), (0, 0, 255))
            self.TerminatedText = self.font.render("TERM:" + str(self.terminated), True, (0, 255, 0), (0, 0, 255))
            self.PowerText = self.font.render(str(self.batteryCharge)  + "Kw Remaining", True, (0, 255, 0), (0, 0, 255))
            self.RechargeText = self.font.render("recharge rate:" + str(self.recharge), True, (0, 255, 0), (0, 0, 255))
            if(self.running == 1):
                self.PowerUseText = self.font.render("Power Use rate:" + str(self.curTask.PowerConsumption), True, (0, 255, 0), (0, 0, 255))
            if(time.time() - self.SunStart >= self.sunChangeTime):
                self.recharge = random.randint(1,1000)
                self.SunStart = time.time()
                self.sunChangeTime - random.randint(1,10)

            # checks if there is no task running if so gets a new one from ready queue
            if(len(self.ready.queue) != 0):
                tempTask = self.ready.get()
                #print(str(self.Bus1553.held) + "1153")
                #print(str(self.VMAbus.held) + "VMA")
                #print(self.running)
                if(self.running == 0 or self.curTask.rmsPriority > tempTask.rmsPriority):
                    if(tempTask.canRun(self.Bus1553,self.VMAbus) == 1):
                        if(self.running == 1):
                            self.ready.insert(self.curTask)
                        self.curTask = self.ready.delete()
                        self.curTask.start(self.Bus1553,self.VMAbus)
                        self.temp += 1
                        self.curTask.StartTime = time.time()
                        self.noTask = 1
                        self.running = 1
                        self.deadLock = 0
                    elif(self.priorityInheritance == 1 and self.curTask.rmsPriority > tempTask.rmsPriority):
                        self.curTask.rmsPriority = tempTask.rmsPriority
                    else:
                        self.deadLock = 1




            #Checks to see if the currently running task has finished executing
            if(self.curTask != None):
                temp = time.time() - self.curTask.StartTime
                #print(temp)

                currentPowerGain = self.recharge - self.curTask.PowerConsumption
                self.TotalPowerText = self.font.render("Total Power Consumption" + str(currentPowerGain), True, (0, 255, 0), (0, 0, 255))
                self.batteryCharge += currentPowerGain * (time.time() - self.start)
                if (self.batteryCharge > 10):
                    self.batteryCharge = 10
                elif (self.batteryCharge <= 0):
                    self.batteryCharge = 0
                    if(self.noPowerStarted == 0):
                        self.NoPowerStart = time.time()
                    self.noPowerStarted = 1
                if(self.batteryCharge != 0 and self.CompPercent <= 100):
                    self.CompPercent = (
                            ((time.time() - self.curTask.StartTime) - self.NoPowerTime) / (self.curTask.compTime))
                    self.CompPercent = round(self.CompPercent, 2)
                   # print(time.time() - self.curTask.StartTime)
                    #print((self.curTask.compTime + self.NoPowerTime))
                    if(self.CompPercent < 1):
                        self.Completion = 200 * self.CompPercent
                    self.CompPercent = 100 * self.CompPercent
                    if (self.CompPercent >= 100):
                        self.CompPercent = 100
                    self.CompText = self.font.render("{:.1f}".format(self.CompPercent), True, (0, 255, 0), (0, 0, 255))
                    self.start = time.time()
                    #print(self.noTask)
                    if (self.noTask == 1 and ((time.time() - self.curTask.StartTime) - self.NoPowerTime) >= (self.curTask.compTime)):
                        if(self.curTask not in self.terminated.queue):
                            #time.sleep(.001)
                            self.curTask.rmsPriority = self.curTask.originalRmsPriority
                            self.noPowerStarted = 0
                            self.NoPowerTime = 0
                            self.NoPowerStart = 0
                            print("task ended" + str(self.curTask))
                            self.curTask.task(self.player,self.VMAbus,self.Bus1553,self)
                            self.curTask.finish(self.Bus1553,self.VMAbus)
                            self.running = 0
                            self.terminated.insert(self.curTask)
                            self.writeFile()
                            if(len(self.ready.queue) == 0):
                                self.curTask = None
                                self.noTask = 0
                    elif((time.time() - self.curTask.StartTime) >= self.curTask.period):
                        self.curTask.rmsPriority = self.curTask.originalRmsPriority
                        self.curTask.StartTime += self.curTask.period
                        self.curTask.finish(self.Bus1553, self.VMAbus)
                        self.noPowerStarted = 0
                        self.NoPowerTime = 0
                        self.NoPowerStart = 0
                        self.running = 0
                        self.DeadlinesMissed += 1
                        #self.terminated.insert(self.curTask)
                        print("missed deadline")
                        if (len(self.ready.queue) == 0):
                            self.curTask = None
                            self.noTask = 0
                else:
                    self.NoPowerTime = time.time() - self.NoPowerStart
                    #print((time.time()) - (self.curTask.StartTime) - (self.curTask.compTime + self.NoPowerTime))
                    #print(self.NoPowerStart)

            #checks if any finished tasks are ready to return to the ready queue
            for x in self.terminated.queue:
                if (time.time() - x.StartTime) >= x.period:
                    x.StartTime += x.period
                    self.ready.insert(x)
                    self.terminated.queue.remove(x)

            for x in self.ready.queue:
                if (time.time() - x.StartTime) >= x.period:
                    x.StartTime += x.period
                    self.DeadlinesMissed += 1
                    print("missed deadline")








            # for x in self.terminated:
            #     if (time.time() - x.ReadyTime >= x.period):
            #         if(x in self.ready.queue):
            #             print("missed deadline")
            #             x.ReadyTime = time.time()
            #         else:
            #             self.ready.insert(x)
            #             print("inserting into ready")
            #             print(self.ready)
            #             x.ReadyTime = time.time()


               # print("Time difference")
               # print(time.time() - self.taskStart)
               # print("comp time")
                #print(self.curTask.compTime)



    def scheduleEDF(self):
            self.ReadyText = self.font.render("READY:" + str(self.ready), True, (0, 255, 0), (0, 0, 255))
            self.CurrentTask = self.font.render(str(self.curTask), True, (0, 255, 0), (0, 0, 255))
            self.TerminatedText = self.font.render("TERM:" + str(self.terminated), True, (0, 255, 0), (0, 0, 255))
            self.RechargeText = self.font.render("recharge rate:" + str(self.recharge), True, (0, 255, 0), (0, 0, 255))
            if(self.running == 1):
                self.PowerUseText = self.font.render("Power Use rate:" + str(self.curTask.PowerConsumption), True,
                                                 (0, 255, 0), (0, 0, 255))
            # checks if there is no task running if so gets a new one from ready queue
            if(len(self.ready.queue) != 0):
                tempTask = self.ready.get()
                #print(self.Bus1553.held)
                if(self.running == 0 or self.curTask.EDFPriority > self.ready.getEDF().EDFPriority):
                    if(tempTask.canRun(self.Bus1553,self.VMAbus) == 1):
                        if(self.running == 1):
                            self.ready.insert(self.curTask)
                        self.curTask = self.ready.delete()
                        self.curTask.start(self.Bus1553,self.VMAbus)
                        self.temp += 1
                        self.curTask.StartTime = time.time()
                        self.noTask = 1
                        self.running = 1
                    elif(self.priorityInheritance == 1 and self.curTask.EDFPriority > self.ready.getEDF()):
                        self.curTask.rmsPriority = tempTask.rmsPriority


            #Checks to see if the currently running task has finished executing
            if(self.curTask != None):
                temp = time.time() - self.curTask.StartTime
                #print(temp)
                self.CompPercent = ((time.time() - self.curTask.StartTime) / self.curTask.compTime)
                currentPowerGain = self.recharge - self.curTask.PowerConsumption
                self.batteryCharge += currentPowerGain*(time.time() - self.start)
                if(self.batteryCharge > 10):
                    self.batteryCharge = 10
                elif(self.batteryCharge < 0):
                    self.batteryCharge = 0
                self.CompPercent = round(self.CompPercent,2)
                self.Completion = 200 * self.CompPercent
                self.CompPercent = 100 * self.CompPercent
                self.CompText = self.font.render("{:.1f}".format(self.CompPercent), True, (0, 255, 0), (0, 0, 255))
                self.start = time.time()
                #print(self.noTask)
                if (self.noTask == 1 and time.time() - self.curTask.StartTime >= self.curTask.compTime):
                    if(self.curTask not in self.terminated.queue):
                        #time.sleep(.001)
                        self.curTask.EDFPriority = self.curTask.originalRmsPriority
                        print(self.curTask.EDFPriority)
                        self.curTask.task(self.player,self.VMAbus,self.Bus1553,self)
                        self.curTask.finish(self.Bus1553,self.VMAbus)
                        self.running = 0
                        self.terminated.insert(self.curTask)
                        self.writeFile()
                        if(len(self.ready.queue) == 0):
                            self.curTask = None
                            self.noTask = 0

            #checks if any finished tasks are ready to return to the ready queue
            for x in self.terminated.queue:
                if (time.time() - x.StartTime) >= x.period:
                    x.StartTime += x.period
                    self.ready.insert(x)
                    self.terminated.queue.remove(x)

            for x in self.ready.queue:
                if (time.time() - x.StartTime) >= x.period:
                    x.StartTime += x.period
                    x.deadLine  += x.period
                    self.DeadlinesMissed += 1
                    print("missed deadline")






            # for x in self.terminated:
            #     if (time.time() - x.ReadyTime >= x.period):
            #         if(x in self.ready.queue):
            #             print("missed deadline")
            #             x.ReadyTime = time.time()
            #         else:
            #             self.ready.insert(x)
            #             print("inserting into ready")
            #             print(self.ready)
            #             x.ReadyTime = time.time()


               # print("Time difference")
               # print(time.time() - self.taskStart)
               # print("comp time")
                #print(self.curTask.compTime)



    def writeFile(self):
        if(self.curTask.name == "Weather Thread"):
            f = open("output.txt", "a")
            f.write("WT,")
            f.close()
        elif(self.curTask.name == "Info Bus Thread"):
            f = open("output.txt", "a")
            f.write("IB,")
            f.close()
        elif (self.curTask.name == "Communication Thread"):
            f = open("output.txt", "a")
            f.write("C,")
            f.close()
        elif (self.curTask.name == "Rotor Control"):
            f = open("output.txt", "a")
            f.write("RC,")
            f.close()
    def priorityCeilingGen(self):
        #find the priority ceiling for VMA
        self.VMAbus.priorityCeiling = min(self.Com.rmsPriority,self.Bus.rmsPriority)
        self.Bus1553.priorityCeiling = min(self.Weather.rmsPriority,self.Bus.rmsPriority)





    def rmsPriorityGen(self):
        TaskList = [self.Weather, self.Bus, self.Com, self.rotor]
        PeriodList = [self.Weather.period, self.Bus.period, self.Com.period, self.rotor.period]
        priority = 0

        # Continue looping while there are periods in the list
        while PeriodList:
            # Find the index of the task with the maximum period
            minPeriod = min(PeriodList)
            minIndex = PeriodList.index(minPeriod)
            TaskList[minIndex].rmsPriority = len(PeriodList)
            #print(maxIndex)

            # Add the corresponding task to the ready list
            TaskList[minIndex].rmsPriority = priority
            TaskList[minIndex].originalRmsPriority = priority
            TaskList[minIndex].EDFPriority = priority
            TaskList[minIndex].originalEDFPriority = priority
            self.ready.insert(TaskList[minIndex])
            priority += 1


            # Remove the selected task and its period from the list
            PeriodList.pop(minIndex)
            TaskList.pop(minIndex)

            # Debug print statement
            #print(self.ready)



class thread():
    def __init__(self,period,compTime,PowerConsumption):
        self.period = period
        self.compTime = compTime
        self.rmsPriority = 0
        self.EDFPriority = 0
        self.originalRmsPriority = 0
        self.PowerConsumption = PowerConsumption
        self.originalEDFPriority = 0
        self.deadLine = period
        self.RRTurnTaken = 0
        self.RRFinished = 0
        self.endTime = 0 #When the task needs to be finished by
        self.StartTime = time.time() #The most recent time the task became ready

    def task(self,player):
        print("place holder")





class WeatherThread(thread):
    def __init__(self,period,compTime,PowerConsumption):
        super().__init__(period,compTime,PowerConsumption)
        self.STATE = "READY"
        self.name = "Weather Thread"
        self.Temp = 10
        #self.deadLine = period
        self.endTime = period
         #the last time the task became avaible

    def WeatherReport(self):
        self.Temp += self.Temp

    def task(self,player,VMA,Bus,schedule):

        self.Temp += 1
        Bus.message = str(self.Temp)
        schedule.BusHeldText = schedule.font.render(str(self.Temp), True, (0, 255, 0), (0, 0, 255))
        #Bus.held = 1

    def canRun(self,Bus,VMA):
        if(Bus.held == 1):
            return 0
        else:
            return 1

    def finish(self,Bus,VMA):
        Bus.held = 0

    def start(self,Bus,VMA):
        Bus.held = 1


    def __str__(self):
        return ("Weather Thread")

class infoBusThread(thread):
    def __init__(self,period,compTime,PowerConsumption):
        super().__init__(period,compTime,PowerConsumption)
        self.STATE = "READY"
        self.name = "Info Bus Thread"
        self.VME = ""
        self.BUS = "" #1153 bus
        self.VMEStatus = 0 # 0 = open 1 = held
        self.BusStatus = 0
        self.endTime = period


    def swap(self):
        #SentData = self.VME
        self.VME = self.BUS
        self.bus = ""
        return self.VME
    def task(self,player,VMA,Bus,schedule):
        # SentData = self.VME
        VMA.message = Bus.message
        schedule.VMAHeldText = schedule.font.render(VMA.message, True, (0, 255, 0), (0, 0, 255))
       # Bus.held = 1
       # VMA.held = 1
    def canRun(self,Bus,VMA):
        if(Bus.held == 1 or VMA.held == 1):
            return 0
        else:
            return 1

    def finish(self,Bus,VMA):
        Bus.held = 0
        VMA.held = 0

    def start(self,Bus,VMA):
        Bus.held = 1
        VMA.held = 1


    def __str__(self):
        return ("Info Bus Thread")

class CommunicationThread(thread):
    def __init__(self, period,compTime,PowerConsumption):
        super().__init__(period,compTime,PowerConsumption)
        self.STATE = "READY"
        self.name = "Communication Thread"
        self.SentData = ""
        self.endTime = period

    def task(self,player,VMA,Bus,schedule):
        schedule.WeatherText = schedule.font.render("Current Temperature on Mars: " + VMA.message + "°C", True, (0, 255, 0), (0, 0, 255))
        print("running")
        #VMA.held = 0

    def canRun(self,Bus,VMA):
        return 1

    def finish(self,Bus,VMA):
        VMA.held = 0

    def start(self,Bus,VMA):
        VMA.held = 1

    def __str__(self):
        return ("Communicaton Thread")

class rotorControl(thread):
    def __init__(self, period,compTime,PowerConsumption):
        super().__init__(period,compTime,PowerConsumption)
        self.name = "Rotor Control"
        self.STATE = "READY"
        self.endTime = period

    def rotate(self):
        random.randrange(0, 360, 3)

    def task(self,player,VMA,Bus,schedule):
        #random.randrange(0, 360, 3)
        player.player_rotation()

    def canRun(self,Bus,VMA):
        return 1

    def start(self,Bus,VMA):
        Bus.held = Bus.held

    def finish(self,Bus,VMA):
        Bus.held = Bus.held

    def __str__(self):
        return ("rotor control")




class register():
    def __init__(self):
        self.message = "none"
        self.held = 0 # set to one if a task is holding the register
        self.priorityCeiling = 0
        self.task = None

# A simple implementation of Priority Queue
# using Queue.
# Taken from Geeks for Geeks
class PriorityQueue(object):
	def __init__(self):
		self.queue = []

	def __str__(self):
		return ' '.join([str(i) for i in self.queue])

	# for checking if the queue is empty
	def isEmpty(self):
		return len(self.queue) == 0

	# for inserting an element in the queue
	def insert(self, data):
		self.queue.append(data)

	# for popping an element based on Priority
	def delete(self):
		try:
			min_val = 0
			for i in range(len(self.queue)):
				if self.queue[i].rmsPriority < self.queue[min_val].rmsPriority:
					min_val = i
			item = self.queue[min_val]
			del self.queue[min_val]
			return item
		except IndexError:
			print()
			exit()

	def deleteEDF(self):
		try:
			min_val = 0
			for i in range(len(self.queue)):
				if self.queue[i].DeadLine < self.queue[min_val].DeadLine:
					min_val = i
			item = self.queue[min_val]
			del self.queue[min_val]
			return item
		except IndexError:
			print()
			exit()

	def getEDF(self):
		try:
			min_val = 0
			for i in range(len(self.queue)):
				if self.queue[i].EDFPriority < self.queue[min_val].EDFPriority:
					min_val = i
			item = self.queue[min_val]
			return item
		except IndexError:
			print()
			exit()

	def get(self):
		try:
			min_val = 0
			for i in range(len(self.queue)):
				if self.queue[i].rmsPriority < self.queue[min_val].rmsPriority:
					min_val = i
			item = self.queue[min_val]
			return item
		except IndexError:
			print()
			exit()


