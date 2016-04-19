"""Controller to manage manipulation of measurement schedules."""
import random
from datetime import datetime

import math

import logging

__author__ = ('hilarious0401@gmail.com (Yikai Lin), chaokong95@gmail.com (Chao Kong)')

from gspeedometer import model
from google.appengine.api import users
from gspeedometer import ResourceMapping

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
    DR = []
    for device in devices:
        properties = device.last_update()
        rem_data = properties.data_limit-properties.data_used
        rem_battery = properties.battery_level-properties.battery_limit
        logging.debug(",".join([str(device.id), str(properties.data_limit),
         str(properties.data_used), str(properties.battery_level), str(properties.battery_limit)]))

        data_D = 0.0
        battery_D = 0.0
        if appetite['data']>rem_data:
            devices.remove(device)
            continue
        else:
            data_D = float(appetite['data'])/rem_data

        if appetite['battery']>rem_battery:
            devices.remove(device)
            continue
        else:
            battery_D = float(appetite['battery']/rem_battery)

        DR.append((device, data_D if data_D>battery_D else battery_D))

    return DR


def dominant():
    if not config:
        return

    task = config.task

    devices = list(task.getSupportedDevices())
    DR = filtr(devices)
    sorted_DR = sorted(DR, key=lambda d:d[1])
    for i in range(len(sorted_DR)):
        logging.debug(str(sorted_DR[i][0].id)+", "+str(sorted_DR[i][1]))

    if len(devices)>0:
        if len(devices)>=config.deviceCount:
            for i in range(config.deviceCount):
                storeTask(sorted_DR[i][0])
        else:
            for i in range(len(devices)):
                storeTask(sorted_DR[i][0])

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
