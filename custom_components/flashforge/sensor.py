"""Flashforge platform for sensor integration."""
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_HOST

import socket
import packets
import parse

BUFFER_SIZE = 1024
TIMEOUT_SECONDS = 5

DOMAIN = "flashforge"

CONF_NAME = "name"
CONF_PORT = "port"
CONF_INCLUDE_INFO = "include_info"
CONF_INCLUDE_HEAD = "include_head"
CONF_INCLUDE_TEMP = "include_temp"
CONF_INCLUDE_PROGRESS = "include_progress"

UNAVAILABLE = 'UNAVAILABLE' # Status used when error connecting to printer

PLATFORM_SCHEMA = {
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=8899): cv.port,
    vol.Optional(CONF_INCLUDE_INFO, default=True): cv.boolean,
    vol.Optional(CONF_INCLUDE_HEAD, default=True): cv.boolean,
    vol.Optional(CONF_INCLUDE_TEMP, default=True): cv.boolean,
    vol.Optional(CONF_INCLUDE_PROGRESS, default=True): cv.boolean
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Flashforge platform."""

    sensor_name = config.get(CONF_NAME)
    printer_address = {'ip': config.get(CONF_HOST), 'port': config.get(CONF_PORT)}
    request_data = [packets.request_control, packets.request_status]
    if config.get(CONF_INCLUDE_INFO):
        request_data.append(packets.request_info)
    if config.get(CONF_INCLUDE_HEAD):
        request_data.append(packets.request_head_position)
    if config.get(CONF_INCLUDE_TEMP):
        request_data.append(packets.request_temp)
    if config.get(CONF_INCLUDE_PROGRESS):
        request_data.append(packets.request_progress)

    add_entities([FlashforgePrinter(sensor_name, printer_address, request_data)])
    return True

class FlashforgePrinter(Entity):
    """Representation of a Flashforge Printer."""

    def __init__(self, sensor_name, printer_address, request_data):
        """Initialize the sensor."""
        self._data = {}
        self._name = sensor_name
        self._request = request_data
        self._printer = printer_address

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

    @property
    def available(self):
        """Return the availability of the sensor."""
        if 'Status' in self._data:
            return self._data['Status'] == UNAVAILABLE
        else:
            return False

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
                    data.update(parse.parse_values(raw_data.decode()))
                printer_socket.shutdown(socket.SHUT_RDWR)
                printer_socket.close()
        except:
            if raw_data == '':
                data['error'] = 'Connection failed.'
            else:
                data['error'] = 'Raw data: ' + raw_data.decode()
        self._data = data
