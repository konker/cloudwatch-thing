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

import utils.audio


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
            self.fetch_current_state()

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


    def fetch_current_state(self):
        # Fetch the alarm state information
        response = self.cloudwatch_client.describe_alarms(
            AlarmNames=[ self.alarm_spec['name'] ],
        )

        if len(response['MetricAlarms']) == 0:
            logging.warn("Could not get current state of alarm")

        self.lastState = response['MetricAlarms'][0]['StateValue']
        if self.lastState == 'ALARM':
            logging.warn('ALARM state detected')
            utils.audio.sound_alarm1()


    def check_alarm(self):
        # Fetch the alarm state information
        response = self.cloudwatch_client.describe_alarm_history(
            AlarmName=self.alarm_spec['name'],
            HistoryItemType='StateUpdate',
            StartDate=datetime.utcnow() - timedelta(seconds=self.alarm_spec['pollDelaySecs']),
            EndDate=datetime.utcnow()
        )

        if len(response['AlarmHistoryItems']) == 0:
            logging.info("No change in state ({})".format(self.lastState))
            if self.lastState == 'ALARM':
                logging.warn('Still in ALARM state')
                utils.audio.sound_alarm1()
            return

        # Check if the alarm has transitioned into an ALARM state
        for i in response['AlarmHistoryItems']:
            history = json.loads(i['HistoryData'])
            oldState = history['oldState']['stateValue']
            newState = history['newState']['stateValue']
            logging.info("State: {} -> {}".format(oldState, newState))

            if newState == 'ALARM':
                logging.warn('ALARM state detected')
                utils.audio.sound_alarm1()

            # Save the new state for comparison
            self.lastState = newState


