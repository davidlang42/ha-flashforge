"""Flashforge platform for sensor integration."""
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT
from homeassistant.helpers.entity import Entity

import socket

REQUEST_CONTROL = '~M601 S1\r\n'
REQUEST_INFO = '~M115\r\n'
REQUEST_HEAD_POSITION = '~M114\r\n'
REQUEST_TEMP = '~M105\r\n'
REQUEST_PROGRESS = '~M27\r\n'
REQUEST_STATUS = '~M119\r\n'

BUFFER_SIZE = 1024
TIMEOUT_SECONDS = 5

DOMAIN = "flashforge"

CONF_DEBUG = "debug"
CONF_INCLUDE_INFO = "include_info"
CONF_INCLUDE_HEAD = "include_head"
CONF_INCLUDE_TEMP = "include_temp"
CONF_INCLUDE_PROGRESS = "include_progress"

UNAVAILABLE = 'UNAVAILABLE' # Status used when error connecting to printer

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=8899): cv.port,
    vol.Optional(CONF_INCLUDE_INFO, default=True): cv.boolean,
    vol.Optional(CONF_INCLUDE_HEAD, default=True): cv.boolean,
    vol.Optional(CONF_INCLUDE_TEMP, default=True): cv.boolean,
    vol.Optional(CONF_INCLUDE_PROGRESS, default=True): cv.boolean,
    vol.Optional(CONF_DEBUG, default=False): cv.boolean
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Flashforge platform."""

    sensor_name = config.get(CONF_NAME)
    printer_address = {'ip': config.get(CONF_HOST), 'port': config.get(CONF_PORT)}
    request_data = [REQUEST_CONTROL, REQUEST_STATUS]
    if config.get(CONF_INCLUDE_INFO):
        request_data.append(REQUEST_INFO)
    if config.get(CONF_INCLUDE_HEAD):
        request_data.append(REQUEST_HEAD_POSITION)
    if config.get(CONF_INCLUDE_TEMP):
        request_data.append(REQUEST_TEMP)
    if config.get(CONF_INCLUDE_PROGRESS):
        request_data.append(REQUEST_PROGRESS)
    debug = config.get(CONF_DEBUG)

    add_entities([FlashforgePrinter(sensor_name, printer_address, request_data, debug)])
    return True

class FlashforgePrinter(Entity):
    """Representation of a Flashforge Printer."""

    def __init__(self, sensor_name, printer_address, request_data, debug):
        """Initialize the sensor."""
        self._data = {}
        self._name = sensor_name
        self._request = request_data
        self._printer = printer_address
        self._debug = debug

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if 'Status' in self._data:
            return self._data['Status']
        else:
            return UNAVAILABLE

    # @property
    # def available(self):
    #     """Return the availability of the sensor."""
    #     if 'Status' in self._data:
    #         return self._data['Status'] == UNAVAILABLE
    #     else:
    #         return False

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return self._data

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        data = {}
        raw_data = ''
        try:
            printer_socket = socket.socket()
            with printer_socket:
                printer_socket.settimeout(TIMEOUT_SECONDS)
                printer_socket.connect((self._printer['ip'], self._printer['port']))
                for message in self._request:
                    printer_socket.send(message.encode())
                    raw_data = printer_socket.recv(BUFFER_SIZE)
                    if self._debug:
                        data['Debug('+message+')'] = raw_data.decode()
                    data.update(parse_values(raw_data.decode()))
                printer_socket.shutdown(socket.SHUT_RDWR)
                printer_socket.close()
        except:
            if raw_data == '':
                data['error'] = 'Connection failed.'
            else:
                data['error'] = 'Raw data: ' + raw_data.decode()
        self._data = data

    def parse_values(text):
        lines = text.split('\r\n')
        values = {}
        for line in lines:
            pair = line.split(':',1)
            if len(pair) == 2:
                values[pair[0]] = pair[1]
        return values