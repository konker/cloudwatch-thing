#!/usr/bin/env python3
#
# cloudwatch-thing daemon
#
# Author: Konrad Markus <konker@iki.fi>
#
#------------------------------------------------------------------------

import os
import sys
import time
import json
import signal
import logging
from pollers.AlarmPoller import AlarmPoller

agents = []


def signal_handler(signal, frame):
    print("Shutting down...")
    for agent in agents:
        agent.stop()


def main():
    from optparse import OptionParser

    # Set up command line options
    parser = OptionParser()
    parser.add_option('-c', '--config', dest='configfile',
                      help='Config JSON file')

    parser.add_option('-d', '--debug', action='store_true', default=False,
                      help='log debugging messages too')

    parser.add_option('-l', '--log', dest='logfile',
                      help='where to send log messages')

    # Do the actual parsing of command line options
    options, args = parser.parse_args()

    if options.debug:
        logging.basicConfig(level=logging.DEBUG,
                            filename=options.logfile,
                            format='%(asctime)s [%(threadName)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
    else:
        logging.basicConfig(level=logging.INFO,
                            filename=options.logfile,
                            format='%(asctime)s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    if not options.configfile:
        parser.error("No config file specified")


    # Read in the config file
    with open(options.configfile) as fp:
        config = json.load(fp)

    # Set up the signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


    # Instantiate an alarm poller for each configured alarm
    for alarm in config['alarms']:
        agent = AlarmPoller(alarm)
        agents.append(agent)
        agent.start()

        # Pause to let the agent get started
        time.sleep(0.5)



if __name__ == '__main__':
    main()
