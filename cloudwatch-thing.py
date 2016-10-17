#!/usr/bin/env python3
#
# cloudwatch-thing
#
# Author: Konrad Markus <konker@iki.fi>
#
#------------------------------------------------------------------------

import boto3
import json
from datetime import datetime
from datetime import timedelta

ALARM_NAME = 'Lambda Errors (konrad)'
POLL_PERIOD_SECS = 60


def main():
    cloudwatch_client = boto3.client('cloudwatch')

    # Fetch the alarm and check its state
    response = cloudwatch_client.describe_alarm_history(
        AlarmName=ALARM_NAME,
        HistoryItemType='StateUpdate',
        StartDate=datetime.utcnow() - timedelta(seconds=POLL_PERIOD_SECS),
        EndDate=datetime.utcnow()
    )
    for i in response['AlarmHistoryItems']:
        history = json.loads(i['HistoryData'])
        oldState = history['oldState']['stateValue']
        newState = history['newState']['stateValue']
        print(oldState, '->', newState)
        if newState == 'ALARM':
            print('BEEP HERE!!!')



if __name__ == '__main__':
    main()



#------------------------------------------------------------------------
# Experiments
    '''
    logs_client = boto3.client('logs')
    '''

    '''
    lambda_client = boto3.client('lambda')
    response = lambda_client.list_functions()
    for f in response['Functions']:
        print(f['FunctionName'])
    '''

    '''
    response = cloudwatch_client.list_metrics()
    for m in response['Metrics']:
        if m['Namespace'] == 'AWS/Lambda' and m['MetricName'] == 'Errors':
            if (is_FunctionName(m, 'MaaS-routes-query')):
                response = cloudwatch_client.get_metric_statistics(
                    Namespace=m['Namespace'],
                    MetricName=m['MetricName'],
                    Dimensions=m['Dimensions'],
                    StartTime=datetime.utcnow() - timedelta(hours=30),
                    EndTime=datetime.utcnow(),
                    Period=120,
                    Statistics=[
                        'Sum'
                    ]
                )
                print(response['Label'])
                for d in response['Datapoints']:
                    print(d)
    '''

'''
def is_FunctionName(metric, name):
    return is_NameValue(metric, 'FunctionName', name)


def is_NameValue(metric, name, value):
    for d in metric['Dimensions']:
        if d['Name'] == name and (d['Value'] == value or value == '*'):
            return True

    return False
'''

