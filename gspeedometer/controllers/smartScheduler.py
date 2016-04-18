"""Controller to manage manipulation of measurement schedules."""
import random
from datetime import datetime

import math

__author__ = ('hilarious0401@gmail.com (Yikai Lin), chaokong95@gmail.com (Chao Kong)')

from gspeedometer import model
from google.appengine.api import users

taskDuration = 3 * 60

config = None


class SmartTask:
    def __init__(self, task, start, end, count):
        self.start = datetime.strptime(start, "%m-%d-%Y %H:%M")
        self.end = datetime.strptime(end, "%m-%d-%Y %H:%M")
        self.deviceCount = count
        self.doneCount = 0
        self.stage = 0
        task.type = task.type[6:]
        self.task = task
        for t in model.Task.all():
            t.delete()


def secondsFromStart():
    d = (datetime.now() - config.start)
    return d.seconds + d.days * 24 * 60 * 60


def secondsToEnd():
    d = (config.end - datetime.now())
    return d.seconds + d.days * 24 * 60 * 60


def totalSeconds():
    d = (config.end - config.start)
    return d.seconds + d.days * 24 * 60 * 60


def schedule(task, start, end, count):
    global config
    config = SmartTask(task, start, end, count)
    dominant()


def totalStages():
    return int(totalSeconds() / taskDuration)


def passedStages():
    return int(secondsFromStart() / taskDuration)


def futureStages():
    return totalStages() - passedStages()


def currentStage():
    return passedStages() + 1

def filtr(devices):
    tasktype = config.task.type
    appetite = ResourceMapping.map(tasktype)
    DR = dict()
    for key, value in appetite.iteritems():
        for device in devices:
            if value>getattr(device, key):
                devices.remove(device)
                continue
            if device in DR:
                if float(value)/getattr(device, key)>DR[device]:
                    DR[device] = float(value)/getattr(device,key)
            else:
                DR[device]=float(value)/getattr(device, key)
    return DR


def dominant():
    if not config:
        return

    task = config.task

    devices = task.getSupportedDevices()
    DR = filtr(devices)
    sorted_DR = sorted(DR, key=DR.__getitem__)

    if len(devices)>0:
        if len(devices)>=config.deviceCount:
            for i in range(config.deviceCount):
                storeTask(sorted_DR[i])
        else:
            for i in range(len(devices)):
                storeTask(sorted_DR[i])

# def tik():
#     if not config:
#         return

#     while config.stage < currentStage():
#         # clear out the existing assignment, recompute the assignment
#         for t in model.Task.all():
#             t.delete()

#         # calculating the # of devices to assign at each stage
#         k = math.ceil((config.deviceCount - config.doneCount) / futureStages())

#         task = config.task
#         devices = sorted(task.getSupportedDevices(), key=lambda d: d.raceStatus())
#         for i in range(0, min(devices.__len__(), k)):
#             storeTask(devices[i])

#         config.stage += 1


def storeTask(device):
    task = config.task
    t = model.Task()
    t.count = task.count
    t.created = task.created
    t.filter = task.filter
    t.tag = task.tag
    t.interval_sec = task.interval_sec
    t.priority = task.priority
    t.start_time = task.start_time
    t.end_time = task.end_time
    t.user = task.user
    t.type = task.type
    t.device = device
    for name, value in task.Params().items():
        setattr(t, 'mparam_' + name, value)
    t.put()


# def mesearmentDone(self):
    # config.doneCount += 1
