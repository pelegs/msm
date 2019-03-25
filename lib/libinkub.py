# For logging
import logging
import logging.config
import json

# For scheduling
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler

# For system calls
from subprocess import call, Popen, PIPE

# For pause
import threading
import time

# For i2cdetect
import re
from subprocess import check_output
import subprocess

# For hardware connections
import smbus
import Adafruit_PCA9685
import bme680
import tcs3400
from DAC5571 import DAC
from i2cio import i2cread, i2cwrite

# For sensor management
from collections import deque
import sys
sys.path.append('library')
import numpy as np

# For light intensity calculations
from round import roundn

# For pause update thread
from gi.repository import GObject, GLib

__version__ = '0.0.3'

#############
# CONSTANTS #
#############

# Conditions
CONDITION_OK = 0
WARNINGS = 1
ERRORS = 2
CONDITION_TEXT = {CONDITION_OK: 'CONDITION OK',
                  WARNINGS: 'WARNINGS',
                  ERRORS: 'ERRORS'}

# For cells
FREE = 0
SELECTED = 1
USED = 2
CELL_STATUS_TEXT = {FREE: 'FREE',
                    SELECTED: 'SELECTED',
                    USED: 'USED'}

# For processes
START  = 1
LIGHT  = 2
DARK   = 3
FINISH = 4
PAUSE  = 5
STATUS_OFF = 0
STATUS_ON = 1
PROCESS_STATUS_TEXT = {START:  'Starting',
                       LIGHT:  'LIGHT',
                       DARK:   'DARK',
                       FINISH: 'Finished',
                       PAUSE:  'Paused'}

# For LEDs
LED_OK = 1
INTENSITY_ERROR = 2
LED_GREEN = 0
LED_RED = 1
LED_YELLOW = 2
LED_ORANGE = 3

# For DAC
START_DAC = 1
STOP_DAC = 2

# For measurements
SET = 0
CALIBRATE = 1
MEASURE = 2
REQUEST_TEXT = {SET: 'SET',
                CALIBRATE: 'CALIBRATE',
                MEASURE: 'MEASURE'}

# For lid
CLOSED = 0
OPEN = 1

###########
# CLASSES #
###########

class condition:
    """ CONDITION

        Keeps track of the condition of the system,
        reports on Warnings and Errors.
    """

    def __init__(self):
        self.warnings = []
        self.errors = []
        self.condition = -1

        self.set_ok()
        self.new_condition = True

    def set_ok(self):
        self.condition = CONDITION_OK
        self.update()
        logger.info('Condition set: OK')

    def add_warning(self, warning):
        self.warnings.append(warning)
        self.asses_condition()
        self.update()
        logger.info('** WARNING **: {}'.format(warning))

    def remove_warning(self):
        self.warnings.pop()
        self.asses_condition()
        self.update()
        logger.info('Removed warning: {}'.format(warning))

    def num_warnings(self):
        return len(self.warnings)

    def add_error(self, error):
        self.errors.append(error)
        self.asses_condition()
        self.update()
        logger.info('** ERROR! ** {}'.format(error))

    def remove_error(self):
        self.errors.pop()
        self.asses_condition()
        self.update()
        logger.info('Removed error: {}'.format(error))

    def num_errors(self):
        return len(self.errors)

    def update(self):
        self.new_condition = True

    def is_updated(self):
        update_backup = self.new_condition
        self.new_condition = False
        return update_backup
    
    def get_condition(self):
        return self.condition

    def asses_condition(self):
        if self.num_errors() > 0:
            logger.info('There are errors')
            self.condition = ERRORS
        else:
            if self.num_warnings() > 0:
                logger.info('There are warnings')
                self.condition = WARNINGS
            else:
                logger.info('No errors nor warnings')
                self.condition = CONDITION_OK

class led:
    """ LED
        
        Represents a group of LED lights (i.e. main lights,
        status lights, etc.).
        Has a unique address and channel, and can be set to
        a pwm frequency and light intensity.
    """
    
    def __init__(self, id, address, channel):
        self.id = id
        self.address = address
        self.channel = channel
        self.pwm_freq = configs['PWM_FREQ']

        self.pwm =     Adafruit_PCA9685.PCA9685(
            address = self.address,
            busnum=1)
        self.pwm.set_pwm_freq(self.pwm_freq)                                

    def set_light_intensity(self, intensity=0):
        if not 0 <= intensity <= 1:
            raise ValueError('Intensity {} not in range [0,1]!'.format(intensity))
            return INTENSITY_ERROR
        else:
            on_fraction = int(intensity * configs['MAX_LED_INTENSITY'])
            self.pwm.set_pwm(self.channel, 0, on_fraction)
            return LED_OK

    def turn_on(self, intensity=0):
        self.set_light_intensity(intensity)

    def turn_off(self):
        self.set_light_intensity(0)

class main_led(led):
    """ MAIN LED
    
        Represents the main LED in the incubator
        (i.e. cell lights).
    """

	def __init__(self, id, address, channel, gain):
		led.__init__(self, id, address, channel)
		self.gain = gain

    def set_light_intensity(self, intensity):
        if not 0 <= intensity <= 40:
            raise ValueError('Intensity {} not in range [0, 40]!'.format(intensity))
            return INTENSITY_ERROR
        
        on_fraction = int(intensity/(self.gain*100.0) * configs['MAX_LED_INTENSITY'])
        on_fraction_int = int(on_fraction)
        self.pwm.set_pwm(self.channel, 0, on_fraction_int)
    
        return LED_OK

class process:
    """ PROCESS

        Holds information about current group status (light, dark),
        and manages events (turn lights on, turn light off, etc.).
    """

    def __init__(self, num_cycles, light_duration, dark_duration, group):
        self.num_cycles = num_cycles
        self.light_duration = light_duration
        self.dark_duration = dark_duration
        self.group = group
        self.parameters = self.group.parameters

        self.events = []
        self.events.append(START)
        for i in range(num_cycles):
            self.events.append(LIGHT)
            self.events.append(DARK)
        self.events.append(FINISH)
    
        self.start_time = datetime.now()

        self.current_event = 0
        self.current_cycle_num = 0
        self.start_process_time = datetime.now() + timedelta(seconds=configs['START_DELAY'])
        self.next_event_time = self.start_process_time
        self.set_next_event()

        self.status = STATUS_ON
        self.pause = False
        logger.info('{}: Finished initialization of process'.format(self.parameters['name']))

    def stop(self):
        self.events = []
        self.status = STATUS_OFF

    def goto_next_event(self):
        logger.info('{}: Going to next event'.format(self.parameters['name']))
        self.current_event += 1
        self.execute_current_event()

    def execute_current_event(self):
        if self.status == STATUS_ON:
            logger.info('{}: Executing current event ({})'.format(self.parameters['name'],
                                                                  PROCESS_STATUS_TEXT[self.events[self.current_event]]))
            if self.events[self.current_event] == LIGHT:
                self.current_cycle_num += 1
                self.group.turn_lights_on()
                self.next_event_time = datetime.now() + timedelta(minutes=self.light_duration)
                self.set_next_event()
                logger.info('{}: Lights on!'.format(self.parameters['name']))
            elif self.events[self.current_event] == DARK:
                self.group.turn_lights_off()
                self.next_event_time = datetime.now() + timedelta(minutes=self.dark_duration)
                self.set_next_event()
                logger.info('{}: Lights off'.format(self.parameters['name']))
            elif self.events[self.current_event] == FINISH:
                self.group.finish_experiment()
                logger.info('{}: Finish experiment'.format(self.parameters['name']))
            self.start_time = datetime.now()
            logger.info('{}: Next event scheduled to {}'.format(datetime.now() + timedelta(minutes=light_duration)))
        else:
            logger.info('{}: msg from the grave'.format(self.parameters['name']))
    
    def set_next_event(self):
        scheduler.add_job(next_event,
                          name='{}'.format(self.parameters['name']),
                          trigger='date',
                          run_date=self.next_event_time,
                          args=[self.group.group_id])
        logger.info('{}: set next event time to {}'.format(self.parameters['name'],
                                                           self.next_event_time))

    def reschedule_next_event(self, dt):
        self.start_time += timedelta(seconds=dt)
        self.next_event_time += timedelta(seconds=dt)
        self.set_next_event()

    def start_pause(self):
        self.pause = True
        for job in scheduler.get_jobs():
            if self.parameters['name'] in job.name:
                scheduler.remove_job(job.id)
        logger.info('{}: next event time was supposed to be {}'.format(self.parameters['name'],
                                                                       self.next_event_time))

    def finish_pause(self):
        self.pause = False

    def get_current_cycle_num(self):
        return self.current_cycle_num

    def get_elapsed_time(self):
        elapsed_time = datetime.now() - self.start_time
        return elapsed_time.total_seconds()

    def get_remaining_time(self):
        remaining_time = self.next_event_time - datetime.now()
        return remaining_time.total_seconds()

    def get_process_duration(self):
        process_duration = self.next_event_time - self.start_time
        return process_duration.total_seconds()

    def get_status(self):
        if self.pause:
            return PROCESS_STATUS_TEXT[PAUSE]
        else:
            return PROCESS_STATUS_TEXT[self.events[self.current_event]]        

class experiment_cell:
    """  INCUBATOR CELL
         
         Has light, temperature, humidity and air quality.
         All are monitored.
    """
    
    def __init__(self, id=-1, light=None, sensor=None):
        self.id = id
        self.light = light
        self.sensor = sensor
        
        self.status = FREE
        self.is_light_on = False
        self.was_light_on = False
        self.target_light_level = 0 

        self.measurements = {
                             'light_level': 0,
                              'temperature': 0,
                             'humidity': 0,
                             'air_quality': 0
                            }

        #self.sensor.calibrate()

    def set_free(self):
        self.status = FREE
    
    def set_used(self):
        self.status = USED
    
    def set_selected(self):
        self.status = SELECTED

    def get_status(self):
        return CELL_STATUS_TEXT[self.status]

    def start_pause(self):
        self.was_light_on = self.is_light_on
        self.turn_light_off()
        logger.info('cell-{} Started pause'.format(self.id))

    def finish_pause(self):
        if self.was_light_on:
            self.turn_light_on(self.target_light_level)
        logger.info('cell-{} Finished pause'.format(self.id))
    
    def turn_light_on(self, light_level):
        self.light.turn_on(light_level)
        self.is_light_on = True
        self.target_light_level = light_level 
        logger.info('cell-{} Light ON (level: {})'.format(self.id, light_level))

    def turn_light_off(self):
        self.light.turn_off()
        self.is_light_on = False 
        logger.info('cell-{} Light OFF'.format(self.id))

    def log_info(self):
        logger.info('LED-{}: pwm={}, channel={}'.format(self.id, self.pwm_group, self.channel))

    def get_sensor_data(self):
        return self.sensor.get_measurements()        

class cell_group:
    """ GROUP OF INCUBATOR CELLS

        Controls between 1 and 13 cells.
    """
    
    def __init__(self, group_id, parameters, cells):
        self.group_id = group_id
        self.parameters = parameters
        self.is_running = False
        self.setup_finished = False
        self.experiment_finished = False # <-- This is somewhat redandent, but kept for code clarity

        # Annex cells    
        self.cells = []
        for cell in cells:
            if cell.status == USED:
                logger.info('Cell {} is already used'.format(cell.id))
                raise ValueError('Cell {} is already used'.format(cell.id))
            else:
                cell.set_used()
                self.add_cell(cell)
        update_active_cells_list()

        # Set temperature if possible
        if self.parameters['temperature'] > 0:
            set_dac(START_DAC, set_temperature=True, temperature=self.parameters['temperature'])

        # Set process
        light_duration_minutes = self.parameters['light_hours'] * 60 + self.parameters['light_mins']
        dark_duration_minutes  = self.parameters['dark_hours']  * 60 + self.parameters['dark_mins']
        self.group_process = process(self.parameters['num_cycles'],
                                     light_duration_minutes,
                                     dark_duration_minutes,
                                     self)
        logger.info('{}: Finished initialization of process (from group)'.format(self.parameters['name']))

        # Finish setup
        self.setup_finished = True
        self.is_running = True
        update_num_running_experiments()
    
    def get_num_cycles(self):
        return self.parameters['num_cycles']

    def set_tab(self, tab):
        self.tab = tab

    def add_cell(self, cell):
        self.cells.append(cell)
        
    def del_cell(self, cell):
        if cell not in self.cells:
            logger.info('Cell {} is not in group {}'.format(cell.id, self.group_id))
            raise ValueError('Cell {} is not in group {}'.format(cell.id, self.group_id))
        else:
            cell.set_free()
            self.cells.remove(cell)
    
    def turn_lights_on(self):
        for cell in self.cells:
            cell.target_light_level = self.parameters['target_light_level']
            cell.turn_light_on(self.parameters['target_light_level'])
    
    def turn_lights_off(self):
        for cell in self.cells:
            cell.target_light_level = 0
            cell.turn_light_off()
        
    def finish_experiment(self):
        # Set temperature if possible
        if self.parameters['temperature'] > 0:
            set_dac(STOP_DAC)
    
        # Turn lights off
        self.turn_lights_off()
    
        # Release cells
        for cell in self.cells:
            cell.turn_light_off()
            cell.set_free()
        update_active_cells_list()

        # Stop light process
        self.group_process.stop()

        # Update tab to finish status 
        self.tab.set_status_finished()
        
        # Update running status
        self.is_running = False
        self.experiment_finished = True
        update_num_running_experiments()
            
        # log
        logger.info('{}, cells {}: experiment ended'.format(
            self.parameters['name'],
            ','.join(map(str, self.parameters['designated_cells_ids'])),
            self.parameters['num_cycles']
            )
        )

    def start_pause(self):
        self.group_process.start_pause()
        for cell in self.cells:
            cell.start_pause()
        logger.info('{}: starting pause'.format(self.parameters['name']))

    def finish_pause(self):
        self.group_process.finish_pause()
        for cell in self.cells:
            cell.finish_pause()
        logger.info('{}: ending pause'.format(self.parameters['name']))
    
    def reschedule(self, dt):
        self.group_process.reschedule_next_event(dt)

    def log_group_jobs(self):
        logger.info('Group {} jobs:'.format(self.parameters['name']))
        for job in scheduler.get_jobs():
            if self.parameters['name'] in job.name:
                logger.info('{}: {}'.format(job.name, job.next_run_time))

    def print_group_parameters(self):
        print('\nNew experiment!')
        print('**********************************')
        print('Experiment name:', self.parameters['name'])
        print('Used cells:', ','.join(map(str, self.parameters['group_cells'])))
        print('Number of cycles:', self.parameters['num_cycles'])
        print('Light time: {} hours and {} minutes'.format(self.parameters['light_hours'],
                                                           self.parameters['light_mins']))
        print('Dark time: {} hours and {} minutes'.format(self.parameters['dark_hours'],
                                                          self.parameters['dark_mins']))
        print('Light level:', self.parameters['light_level'])
        print('Temperature: {} C'.format(self.parameters['temperature']))
        for i, cycle in enumerate(self.cycles):
            print('cycle-{} light on at {}'.format(i+1, cycle.start_datetime))
            print('cycle-{} light off at {}'.format(i+1, cycle.dark_start_datetime))
        print('**********************************')

class cell_sensor:
    """ CELL SENSOR
        
        Measures temperature, humidity, pressure,
        air quality and light level and color.

        Variables:
        * id: unique software identifier
        * multiplexer_addr: address for multiplexer
                            (there are two of them)
        * data_byte: unique hardware identifier
    """

    def __init__(self, id, multiplexer_addr, data_byte):
        self.id = id
        self.multiplexer_addr = multiplexer_addr
        # data_byte is sensor address
        self.data_byte = data_byte
        self.a_coeff = configs['A_COEFFS'][id]
        self.b_coeff = configs['B_COEFFS'][id]

        # Magic reset part-1
        set_multiplexer_channel(self.multiplexer_addr, self.data_byte)
        logger.info('0x74: {}, 0x75: {}'.format(hex(i2cread(0x74)), hex(i2cread(0x75))))
        
        # Set BME device
        self.bme_address = configs['BME_ADDR']
        self.bme_device = bme680.BME680(i2c_addr=self.bme_address)
        self.active = False
        self.calibrated = False
        self.properties_set = False
        self.air_quality_score = 0

        # Set TCS3400 device
        self.tcs_address = configs['TCS_ADDR']
        self.tcs_device = tcs3400.TCS3400(address=self.tcs_address)

        # Storing data
        self.measurements_dict = {'temperature': -1,
                      'humidity': -1,
                      'pressure': -1,
                      'air_quality': -1,
                      'ir':    -1,
                      'rgb': [-1, -1, -1],
                      'light_level': -1}

        # For calibration
        self.burn_in_data = []

    def get_info(self):
        return 'Sensor-{}: Main address: {}, multiplexer address: {},\nchannel: {}, set: {}'.format(
                self.id,
                hex(self.bme_address),
                hex(self.multiplexer_addr),
                hex(self.data_byte),
                self.properties_set,
                )

    def calibrate(self):
        self.active = True
        logger.info('Calibrating sensor {}...'.format(self.id))
        
        # Set multiplexers to correct channels
        set_multiplexer_channel(self.multiplexer_addr, self.data_byte)
        logger.info('0x74: {}, 0x75: {}'.format(hex(i2cread(0x74)), hex(i2cread(0x75))))
        
        # TCS DEVICE
        self.tcs_device.set_properties(gain=configs['MAIN_LED_GAIN'])
        
        # ALL SET
        self.properties_set = True
        
        # BME DEVICE
        # Oversampling
        logger.info('setting properties for sensor {}'.format(self.id))
        self.bme_device.set_humidity_oversample(bme680.OS_2X)
        self.bme_device.set_pressure_oversample(bme680.OS_4X)
        self.bme_device.set_temperature_oversample(bme680.OS_8X)
        self.bme_device.set_filter(bme680.FILTER_SIZE_3)
        self.bme_device.set_gas_status(bme680.ENABLE_GAS_MEAS)
        logger.info('sensor {} set'.format(self.id))

        # perform calibration
        num_points = configs['BME_CALIB_POINTS']
        while len(self.burn_in_data) < configs['BME_CALIB_POINTS']:
            if self.bme_device.get_sensor_data():# and self.bme_device.data.heat_stable:
                gas = self.bme_device.data.gas_resistance
                self.burn_in_data.append(gas)
                logger.info('sensor {}: adding calibration point ({} out of {})'.format(
                    self.id,
                    len(self.burn_in_data),
                    num_points))
                time.sleep(1)
        self.gas_baseline = sum(self.burn_in_data[-num_points:]) / float(num_points)
        # Set the humidity baseline to 40%, an optimal indoor humidity
        self.hum_baseline = 40.0
        # This sets the balance between humidity and gas reading in the 
        # calculation of air_quality_score (25:75, humidity:gas)
        self.hum_weighting = 0.25
        
        # Define properties for heater calibration
        # (needed for air quality measurements)    
        self.bme_device.set_gas_heater_temperature(320)
        self.bme_device.set_gas_heater_duration(150)
        self.bme_device.select_gas_heater_profile(0)
        
        logger.info('Sensor {} is calibrated'.format(self.id))
        self.calibrated = True
        self.active = False
        
    def perform_measurements(self):
        """ Performs measurements, and saves
            them to self.measurements_dict.
            This code is based on an example
            from the BME python library.
        """
        
        # Set flag active to true, telling the
        # Sensor manager to wait before switching
        # to the next sensor
        self.active = True    
        
        if not self.calibrated:
            raise Warning('Sensor {} is not calibrated, yet a measurement was requested'.format(self.id))

        if self.bme_device.get_sensor_data() and self.bme_device.data.heat_stable:
            gas = self.bme_device.data.gas_resistance
            gas_offset = self.gas_baseline - gas
            
            hum = self.bme_device.data.humidity
            hum_offset = hum - self.hum_baseline
            
            # Calculate hum_score as the distance from the hum_baseline
            if hum_offset > 0:
                hum_score = (100 - self.hum_baseline - hum_offset) / (100 - self.hum_baseline) * (self.hum_weighting * 100)
            
            else:
                hum_score = (self.hum_baseline + hum_offset) / self.hum_baseline * (self.hum_weighting * 100)
            
            # Calculate gas_score as the distance from the gas_baseline
            if gas_offset > 0:
                gas_score = (gas / self.gas_baseline) * (100 - (self.hum_weighting * 100))
            
            else:
                gas_score = 100 - (self.hum_weighting * 100)
            
            # Calculate air_quality_score 
            self.air_quality_score = hum_score + gas_score
        
        # Get temperature, humidity and pressure from BME
        if self.tcs_device.get_sensor_data():
            self.measurements_dict['temperature'] = self.bme_device.data.temperature
            self.measurements_dict['humidity'] = self.bme_device.data.humidity
            self.measurements_dict['pressure'] = self.bme_device.data.pressure
            self.measurements_dict['air_quality'] = self.air_quality_score

            # Calculate light intensity in mW
            # (using quadratic formula)
            self.measurements_dict['ir']  = self.tcs_device.ir
            self.measurements_dict['rgb'] = self.tcs_device.rgb
            y = self.tcs_device.intensity
            a = self.a_coeff
            b = self.b_coeff
            self.measurements_dict['light_level'] = (np.sqrt(b**2.0+4*a*y)-b)/(2*a)

        # Set flag active to false, allowing the
        # Sensor manager to switch to the next sensor
        self.active = False

    def get_measurements(self):
        return self.measurements_dict

###########
# THREADS #
###########

class condition_thread(threading.Thread):
    """ CONDITION THREAD

        Follows system condition (ok, warnings, errors) 
        and switches status LEDs accordingly.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()

    def run(self):
        while not self.stopped():
            if system_condition.is_updated():
                sys_condition = system_condition.get_condition()
                update_condition(sys_condition)
            time.sleep(1)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class pause_thread(threading.Thread):
    """ PAUSE THREAD

        Performs writing elapsed pause time in the pause window.
    """

    def __init__(self, pause_window, start_time):
        threading.Thread.__init__(self)
        self.pause_window = pause_window
        self.start_time = start_time
        self._stop_event = threading.Event()

    def run(self):
        while not self.stopped():
            time.sleep(1)
            time_text = str(datetime.now()-self.start_time).split('.')[0]
            GLib.idle_add(self.pause_window.update_time, time_text)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class sensor_managing_thread(threading.Thread):
    """ SENSOR MANAGING (SM) THREAD

        Continuesly loops over sensors, telling
        them to take measurements.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()

    def run(self):
        while not self.stopped():
            for cell in active_cells_list:
                sensor = cell.sensor

                # Set multiplexer address and channel to correct sensor
                set_multiplexer_channel(sensor.multiplexer_addr, sensor.data_byte)
                
                # Tell sensor to measure data
                sensor.perform_measurements()
        
                # Wait until sensor finished measurements
                while sensor.active:
                    pass

    def stop(self):
        logger.info('SM stopped')
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

#############
# FUNCTIONS #
#############

def update_condition(condition):
    for led in status_leds:
        led.turn_off()
    if condition == ERRORS:
        status_leds[LED_RED].turn_on(1)
    if condition == WARNINGS:
        status_leds[LED_YELLOW].turn_on(1)
    if condition == CONDITION_OK:
        status_leds[LED_GREEN].turn_on(1)

def set_dac(dac_action, set_temperature=False, temperature=20):
    # Set the 7th and 8th bits of the I/O Exapnder to 0
    # (i.e. turning the DAC on)
    old_val = i2cread(configs['IO_EXPANDER_ADDR'])

    mask = 0b11000100
    if dac_action == START_DAC:
        new_val = 0b00000100
        logger.info('*** DAC Started ***')
    else:
        new_val = 0b11000100
        logger.info('*** DAC Stopped ***')
    i2cwrite(configs['IO_EXPANDER_ADDR'], (old_val & ~mask) | (new_val & mask))
    
    # Setting dac to proper voltage
    if set_temperature:
        dac_V = temperature * configs['dac_m'] + configs['dac_b']
        logger.info('*** Setting DAC voltage to {} ***'.format(dac_V))
        dac.setV(dac_V)

def lid_open():
    read = i2cread(configs['IO_EXPANDER_ADDR'])
    open = (1 << 2) & read
    if open:
        return True
    else:
        return False

""" This is an absolutly terrible HACK, but apparantly it's NOT
    possible to call internal functions from the scheduler :-/
"""
def next_event(group_id):
    groups[group_id].group_process.goto_next_event()
"""
"""

def delete_jobs(name):
    """ Deletes all jobs with name 'name' """
    for job in scheduler.get_jobs():
        if name in job.name:
            scheduler.remove_job(job.id) 

def set_sensor(bus, channel):
    bus.write_byte(configs['MLTPLX_ADDR'], multiplexer[channel])

def set_multiplexer_channel(multiplexer_addr, channel):
    """ Sets a multiplexer (either 0x74 or 0x75) to desired channel.
        The other multiplexer is set to channel 0x0 to avoid collision.
    """
    if multiplexer_addr == 0x74:
        i2cwrite(0x74, channel)
        i2cwrite(0x75, 0x00)
    elif multiplexer_addr == 0x75:
        i2cwrite(0x74, 0x00)
        i2cwrite(0x75, channel)
    else:
        raise Warning('No multiplexer on address {}'.format(multiplexer_addr))

def load_config(filename):
    # Load configurations
    import configparser    
    config = configparser.ConfigParser()
    config.read(filename)

    config_dict = {}

    # [BUS]
    bus_config = config['BUS']
    config_dict['BUS_NUM'] = int(bus_config['bus_num'])
    config_dict['IO_EXPANDER_ADDR'] = int(bus_config['io_expander_addr'], 16)
    config_dict['MLTPLX_ADDR1'] = int(bus_config['multiplexer_addr1'], 16)
    config_dict['MLTPLX_ADDR2'] = int(bus_config['multiplexer_addr2'], 16)
    config_dict['MLTPLX_GROUPS'] = [group for group in bus_config['multiplexer_groups'].split(',')]
    config_dict['MLTPLX_CHANNEL'] = [int(channel, 16) for channel in bus_config['multiplexer_channels'].split(',')]
    config_dict['DAC_ADDR'] = int(bus_config['DAC_addr'], 16)

    # [LED]
    led_config = config['LEDS']
    config_dict['MAX_LED_INTENSITY'] = int(led_config['max_led_intensity'])
    config_dict['MAIN_LED_GAIN'] = int(led_config['main_led_gain'])
    config_dict['MAIN_LED_GROUPS'] = [group for group in led_config['main_led_groups'].split(',')]
    config_dict['LED_GROUP_ADDRESS'] = {'A1': int(led_config['a1_addr'], 16),
                                        'A2': int(led_config['a2_addr'], 16),
                                         'B1': int(led_config['b1_addr'], 16),
                                         'B2': int(led_config['b2_addr'], 16)}
    config_dict['MAIN_LED_ADDRESS'] = [config_dict['LED_GROUP_ADDRESS'][group] for group in config_dict['MAIN_LED_GROUPS']]
    config_dict['LED_GROUP_INDECES'] = {'A1': 0, 'A2': 1, 'B1': 2, 'B2': 3}
    config_dict['MAIN_LED_CHANNELS']   = [int(val) for val in led_config['main_led_channels'].split(',')]
    config_dict['STATUS_LED_ADDRESS']  = int(led_config['status_led_address'], 16)
    config_dict['STATUS_LED_CHANNELS'] = [int(val) for val in led_config['status_led_channels'].split(',')]
    config_dict['HELPER_LED_CHANNEL']  = [int(val) for val in led_config['helper_led_channel'].split(',')]
    config_dict['PWM_FREQ'] = int(led_config['PWM_FREQ'])
    config_dict['I2mW'] = [float(x) for x in led_config['I2mW'].split(',')]
    config_dict['STATUS_LED_COLORS'] = led_config['status_led_colors'].split(',')
    config_dict['STATUS_LED_CHANNELS_BY_COLOR'] = {key:val for key, val in zip(config_dict['STATUS_LED_COLORS'],
                                                                               config_dict['STATUS_LED_CHANNELS'])}
    config_dict['STATUS_LED_START_SCRIPT'] = [cmd for cmd in led_config['status_led_start_script'].split(',')]
    config_dict['STATUS_LED_END_SCRIPT'] = [cmd for cmd in led_config['status_led_end_script'].split(',')]

    # [DAC]
    dac_config = config['DAC']
    config_dict['dac_m'] = float(dac_config['dac_m'])
    config_dict['dac_b'] = float(dac_config['dac_b'])

    # [SENSORS]
    sensors_config = config['SENSORS']
    config_dict['BME_ADDR'] = int(sensors_config['bme_address'], 16)
    config_dict['BME_CALIB_POINTS'] = int(sensors_config['bme_calibration_time'])
    config_dict['TCS_ADDR'] = int(sensors_config['tcs_address'], 16)
    config_dict['A_COEFFS'] = [float(x) for x in sensors_config['a_coeffs'].split(',')]
    config_dict['B_COEFFS'] = [float(x) for x in sensors_config['b_coeffs'].split(',')]

    # [TIME]
    config_dict['START_DELAY'] = int(config['TIME']['start_delay'])
    config_dict['MISFIRE_GRACE'] = int(config['TIME']['misfire_grace'])

    # [USERS]
    users = config['USERS']['users'].split(',')
    config_dict['USERS'] = {key: 0 for key in users}
    
    # [GUI]
    gui_config = config['GUI']
    config_dict['SIZE_X'] = int(gui_config['size_x'])
    config_dict['SIZE_Y'] = int(gui_config['size_y'])
    config_dict['MARGINS'] = {'TOP': int(gui_config['margin_top']),
                              'BOTTOM': int(gui_config['margin_bottom']),
                              'LEFT': int(gui_config['margin_left']),
                              'RIGHT': int(gui_config['margin_right'])}

    # [BUTTONS]
    buttons_config = config['BUTTONS']
    buttons_lib = buttons_config['LIB'] + '/'
    config_dict['CELL_BUTTON_ICONS'] = [buttons_lib + val for val in buttons_config['cell_button_icons'].split(',')]
    config_dict['NEW_ICON'] = buttons_lib + buttons_config['new_icon']
    config_dict['PAUSE_ICON'] = buttons_lib + buttons_config['pause_icon']
    config_dict['STOP_ICON'] = buttons_lib + buttons_config['stop_icon']
    config_dict['CONTINUE_BUTTON_ICON'] = buttons_lib + buttons_config['continue_icon']
    config_dict['EXIT_ICON'] = buttons_lib + buttons_config['exit_icon']
    config_dict['ABOUT_ICON'] = buttons_lib + buttons_config['about_icon']
    config_dict['START_ICON'] = buttons_lib + buttons_config['start_icon']
    config_dict['CANCEL_ICON'] = buttons_lib + buttons_config['cancel_icon']
    config_dict['BACK_ICON'] = buttons_lib + buttons_config['back_icon']
    config_dict['STOP_ICON_REV'] = buttons_lib + buttons_config['stop_icon_rev']
    config_dict['FINISH_ICON'] = buttons_lib + buttons_config['finish_icon']
    config_dict['CLOSE_TAB_ICON'] = buttons_lib + buttons_config['close_tab_icon']
    config_dict['IO_TOGGLE_OFF'] = buttons_lib + buttons_config['io_toggle_off']
    config_dict['IO_TOGGLE_ON'] = buttons_lib + buttons_config['io_toggle_on']
    config_dict['EXIT_ICON_GREEN'] = buttons_lib + buttons_config['exit_icon_green']
    config_dict['BACK_ICON_BLUE'] = buttons_lib + buttons_config['back_icon_blue']

    # [IMAGES]
    img_config = config['IMAGES']
    img_lib = img_config['lib'] + '/'
    config_dict['PAUSE_IMG'] = img_lib + img_config['pause']
    config_dict['WARNING'] = img_lib + img_config['warning']
    config_dict['WARNING_SINGLE'] = img_lib + img_config['warning_single']
    config_dict['EXIT_PROMPT'] = img_lib + img_config['exit_prompt']
    config_dict['LIGHT_IMG'] = img_lib + img_config['light_img']
    config_dict['DARK_IMG'] = img_lib + img_config['dark_img']
    config_dict['LID_OPEN_IMG'] = img_lib + img_config['lid_open_img']
    config_dict['ABOUT_IMG'] = img_lib + img_config['about_img']
    config_dict['EXP_PREP_IMG'] = img_lib + img_config['exp_prep_img']
    
    return config_dict

def start_pause():
    """ Start pause: pauses the scheduler so no jobs would
        be executed and shuts down all lights and heating/cooling
        in all cells (via the I/O Exapnder).
    """
    
    scheduler.pause()
    for group in groups:
        group.start_pause()
    
    set_dac(STOP_DAC)

def finish_pause():
    """ Finishes pause: resumes the scheduler,
        all groups' work and heating/cooling.
    """
    
    set_dac(START_DAC)
    
    scheduler.resume()
    for group in groups:
        group.finish_pause()

def reschedule(dt):
    """ Used for pause. dt is in seconds. """

    logger.info('Pause lasted {} seconds'.format(dt))    
    for group in groups:
        group.reschedule(dt)

def turn_off():
    """ Switch off all that is needed before
        closing the program (cells, threads, etc.).
    """
    # Blink goodbye morse code
    #parse_led_script('end')

    # Close threads
    SM_thread.stop()
    sys_condition_thread.stop()
    sys_condition_thread.join()

    # Set I/O Exapnder to 0xc0
    i2cwrite(configs['IO_EXPANDER_ADDR'], 0xFF)

    # Turn off all cells
    for cell in cells:
        cell.turn_light_off()

    print('Goodbye!')

def i2cdetect(busaddr=1, first=0x03, last=0x77):
    """ Detects all devices connected to the i2c bus
        and returns their addresses in a list.

        It runs i2cdetect on a specific bus (default=1) and specific
        first and last addresses (default: 0x03 and 0x77, respectively).
        The output is then split by endline and matched to a regex pattern
        (two hex digits without ':' after them).
    """
    p = str(check_output(['i2cdetect', '-y',
                          str(busaddr), hex(first), hex(last)])).split('\\n')[1:-1]
    addresses = [int(match[:-1], 16) for line in p
                            for match in re.findall('[a-f0-9]{2}[^:]', line)]
    return addresses

def update_active_cells_list():
    active_cells_list = [cell for cell in cells if cell.status==USED ]
    logger.info('Active cells: {}'.format(','.join(map(str, [cell.id for cell in active_cells_list]))))

def get_num_running_experiments():
    return sum([1 if group.is_running else 0 for group in groups])

def update_num_running_experiments():
    num_running_experiments = get_num_running_experiments()
    logger.info('Number of running experiments: {}'.format(num_running_experiments))
    if num_running_experiments > 0:
        status_leds[LED_ORANGE].turn_on(1)    
    else:
        status_leds[LED_ORANGE].turn_off()    

def parse_led_script(position='start'):
    if position == 'start':
        script = configs['STATUS_LED_START_SCRIPT']
        factor = 1000.0
    elif position == 'end':
        script = configs['STATUS_LED_END_SCRIPT']
        factor = 1000.0
    else:
        raise ValueError('Status LED script must be \'start\' or \'end\'! \'{}\' is unkown.'.format(position))

    for cmd in script:
        scmd = cmd.split(':')
        leds = [int(channel) for channel in scmd[0]]
        duration = float(scmd[1]) / factor
        for led in leds:
            if led != 4:
                status_leds[led].turn_on(intensity=1)
            time.sleep(duration)
        for status_led in status_leds:
            status_led.turn_off()

##################
# INITIALIZATION #
##################

# Start logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('inkub')
logger.info('')
logger.info('** Program started **')

# Load configs
configs = load_config('config')
logger.info('Configurations loaded')

# Bus initialization
Bus = smbus.SMBus(1)
logger.info('Bus initialized')

# Set IO Expander to all 1s
Bus.write_byte(configs['IO_EXPANDER_ADDR'], 0xFF)

# LEDs initialization
main_leds = []
for i in range(13):
    main_leds.append(main_led(id = i,
                              address=configs['MAIN_LED_ADDRESS'][i],
                              channel=configs['MAIN_LED_CHANNELS'][i]))

status_leds = []
for i in range(4):
    status_leds.append(led(id = i,
                           address=configs['STATUS_LED_ADDRESS'],
                           channel=configs['STATUS_LED_CHANNELS'][i]))

logger.info('LEDs initialized')

# Startup led script
parse_led_script('start')

# DAC controler
dac = DAC(Bus, configs['DAC_ADDR'], mode=0)
logger.info('DAC initialized')

# Scheduler initialization
call(['rm', '-f', 'schedules.sqlite'])
url = 'sqlite:///schedules.sqlite'
scheduler = BackgroundScheduler(job_defaults={'misfire_grace_time': configs['MISFIRE_GRACE']})
scheduler.add_jobstore('sqlalchemy', url=url)
scheduler.start()
logger.info('Scheduler initialized and started')

# Sensors initialization
sensor_groups = {'m1': configs['MLTPLX_ADDR1'],
                 'm2': configs['MLTPLX_ADDR2']}
cell_sensors = [cell_sensor(id=i,
                          multiplexer_addr=sensor_groups[configs['MLTPLX_GROUPS'][i]],
                          data_byte=configs['MLTPLX_CHANNEL'][i])
               for i in range(13)]

# Sensor calibration
for sensor in cell_sensors:
    sensor.calibrate()
    while sensor.active:
        time.sleep(0.1)
logger.info('Sensors initialized:')
for sensor in cell_sensors:
    logger.info(sensor.get_info())

# Cells initialization
cells = [experiment_cell(id=i,
                         light=main_leds[i],
                         sensor=cell_sensors[i])
         for i in range(13)]
selected_cells = set()
groups = []
logger.info('Cell objects initialized')
num_running_experiments = 0
active_cells_list = []

# Sensor Manager (SM) initialization
SM_thread = sensor_managing_thread()
SM_thread.start()
logger.info('Sensor Manager initialized')

# Users initialization
users = configs['USERS']
logger.info('Users set')

# System condition tracking
system_condition = condition()
sys_condition_thread = condition_thread()
sys_condition_thread.start()
logger.info('Condition thread initialized')

# Lid status check
current_lid_status = CLOSED

# Global pause status    
global_pause = False
