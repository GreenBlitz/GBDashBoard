import gbrpi
import subprocess

from gbdashboard.constants.ports import LED_RING_PORT

leds = gbrpi.LedRing(LED_RING_PORT)


def set_led_state(state):
    if state:
        leds.on()
    else:
        leds.off()


def set_exposure_state(raw: int, camera: int):
    subprocess.call(['v4l2-ctl', '-d', f'/dev/video{camera}', '-c', f'exposure_absolute={raw}'])


def set_auto_exposure_state(raw: int, camera: int):
    subprocess.call(['v4l2-ctl', '-d', f'/dev/video{camera}', '-c', f'exposure_auto={raw}'])
