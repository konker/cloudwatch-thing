#
# cloudwatch-thing daemon
#
# Author: Konrad Markus <konker@iki.fi>
#
#------------------------------------------------------------------------

import boto3
import time
import json
import logging
from threading import Thread
from datetime import datetime
from datetime import timedelta


class AlarmPoller:
    def __init__(self, alarm_spec):
        self.alarm_spec = alarm_spec
        self.alive = False
        self.interrupt_flag = False
        self.thread = None
        self.lastState = None
        self.cloudwatch_client = boto3.client('cloudwatch')


    def start(self):
        logging.info('AlarmPoller {} started'.format(self.alarm_spec['id']))
        try:
            self.thread = Thread(target=self._run)
            self.thread.start()
        except:
            logging.info('AlarmPoller {} stopped'.format(self.alarm_spec['id']))


    def stop(self):
        self.alive = False
        if self.thread:
            self.thread.join(2)


    def interrupt(self):
        if self.alive:
            self.interrupt_flag = True


    def _run(self):
        self.alive = True
        try:
            while self.alive:
                self.check_alarm()
                for i in range(self.alarm_spec['pollDelaySecs']):
                    if not self.alive:
                        break

                    if self.interrupt_flag:
                        self.interrupt_flag = False
                        break

                    time.sleep(1)

            # Once we have finished the main loop
            logging.info('AlarmPoller {} stopped'.format(self.alarm_spec['id']))

        except Exception as ex:
            logging.info('AlarmPoller {} stopped'.format(self.alarm_spec['id']))
            logging.exception(ex)


    def check_alarm(self):
        cloudwatch_client = boto3.client('cloudwatch')

        # Fetch the alarm state information
        response = cloudwatch_client.describe_alarm_history(
            AlarmName=self.alarm_spec['name'],
            HistoryItemType='StateUpdate',
            StartDate=datetime.utcnow() - timedelta(seconds=self.alarm_spec['pollDelaySecs']),
            EndDate=datetime.utcnow()
        )

        # Check if the alarm has transitioned into an ALARM state
        for i in response['AlarmHistoryItems']:
            history = json.loads(i['HistoryData'])
            oldState = history['oldState']['stateValue']
            newState = history['newState']['stateValue']
            logging.info("State: {} -> {}".format(oldState, newState))

            if newState == 'ALARM':
                logging.warn('BEEP HERE!!!')

