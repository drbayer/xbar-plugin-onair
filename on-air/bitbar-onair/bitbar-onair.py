#!/usr/bin/env PYTHONIOENCODING=UTF-8 python3

import time
import os
import subprocess
import magichue
import configparser
import logging


config_file = "bitbar-onair.conf"
exec_dir = os.path.dirname(os.path.abspath(__file__))

config_defaults = {
    "default": {
        "lights": "first",
        "logfile": "STDOUT",
        "loglevel": "none"
    },
    "on-air": {
        "light-on": "true",
        "transition": "NORMAL",
        "r": "255",
        "g": "0",
        "b": "0",
        "brightness": "255"
        },
    "off-air": {
        "light-on": "true",
        "transition": "NORMAL",
        "r": "0",
        "g": "255",
        "b": "0",
        "brightness": "255"
        }
}


def get_config():
    config = configparser.ConfigParser()
    config.read_dict(config_defaults)
    config.read(os.path.join(exec_dir, config_file))
    return config


def get_rgbtuple(state):
    r = config[state].getint('r')
    g = config[state].getint('g')
    b = config[state].getint('b')
    return (r, g, b)


def tuple2hex(color):
    (r, g, b) = color
    return '#%02x%02x%02x' % (r, g, b)


def in_meeting():
    in_meeting = False
    processes = subprocess.Popen(['lsof', '-i', '4UDP'],
                                 stdout=subprocess.PIPE).stdout.readlines()
    for process in processes:
        if 'zoom' in str(process):
            in_meeting = True
            break
    return in_meeting


def get_onair_lights():
    addresses = config['default']['lights'].split(',')
    logger.debug("Looking for lights at address(es) %s" % (addresses))
    lights = []
    if addresses[0] == 'first':
        lights_found = magichue.discover_bulbs()
        try:
            lights.append(magichue.Light(lights_found[0]))
        except Exception as e:
            logger.error('On-Air light not found: %s' % (str(e)))
    else:
        for address in addresses:
            # Trying to connect to a light that doesn't exist takes a long
            # time, so ping it first to avoid errors in config
            if not subprocess.run(['ping', '-c', '1', '-t', '1', address],
                                  stdout=subprocess.DEVNULL).returncode == 0:
                logger.error('Light not found at address %s' % (address))
                continue
            try:
                lights.append(magichue.Light(address))
                logger.debug('Light found at %s' % (address))
            except ConnectionRefusedError:
                logger.error('Connection refused for light at %s' % (address))
            except Exception as e:
                logger.error('Unable to connect to light at %s: %s'
                             % (address, str(e)))
    return lights


def set_light_state(light, state):
    rgb = get_rgbtuple(state)
    light_on = config[state].getboolean('light-on')
    brightness = config[state].getint('brightness')
    transition_effect = getattr(magichue, config[state]['transition'].upper())
    if not light.on == light_on:
        logger.info('Setting state of light %s to light.on = %s' %
                    (light.addr, str(light_on)))
        light.on = light_on
    if light_on:
        light.is_white = False
        light.mode = transition_effect
        time.sleep(light.speed)
        light.rgb = rgb
        light.brightness = brightness
        logger.debug('Set light %s rgb = %s and brightness = %s' %
                     (light.addr, tuple2hex(rgb), str(brightness)))


if __name__ == "__main__":
    config = get_config()
    # Set up logging
    logger = logging.getLogger()
    if config['default']['loglevel'].upper() == 'NONE':
        log_handler = logging.NullHandler()
    else:
        numeric_loglevel = getattr(logging,
                                   config['default']['loglevel'].upper())
        logger.setLevel(numeric_loglevel)
        log_handler = logging.FileHandler('bitbar-onair.log',
                                          encoding='utf-8')
        log_handler.setLevel(numeric_loglevel)
        log_format = '%(asctime)s [%(levelname)s] %(message)s'
        formatter = logging.Formatter(log_format)
        log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    lights = get_onair_lights()
    state = 'on-air' if in_meeting() else 'off-air'
    state_label = state.replace('-', ' ').upper()
    state_color = tuple2hex(get_rgbtuple(state))

    print("🎙️ %s | color=%s" % (state_label, state_color))
    print('---')
    for light in lights:
        set_light_state(light, state)
        print("Light %s %s | color=%s" %
              (light.addr, state_label, state_color))
