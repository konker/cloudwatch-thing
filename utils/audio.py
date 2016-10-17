#
# cloudwatch-thing audio utils
#
# Author: Konrad Markus <konker@iki.fi>
#
#------------------------------------------------------------------------

import time
from utils import utils
try:
    import RPi.GPIO as GPIO
except:
    pass


RPI_ALARM_PIN = 12
FREQUENCIES_ALARM1 = [900, 600]


def sound_alarm1():
    if utils.is_rpi():
        rpi_sound_alarm1()
    else:
        other_sound_alarm1()


def other_sound_alarm1():
    #[TODO]
    print("---------------------> BEEP BEEP!")


def rpi_sound_alarm1():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RPI_ALARM_PIN, GPIO.OUT)

    pwm = GPIO.PWM(RPI_ALARM_PIN, FREQUENCIES_ALARM1[0])
    pwm.start(0)

    pwm.ChangeDutyCycle(50)

    for i in range(3):
        for frequency in FREQUENCIES_ALARM1:
            pwm.ChangeFrequency(frequency)
            time.sleep(0.5)

    pwm.stop()
    GPIO.cleanup()


