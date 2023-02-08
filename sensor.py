"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import POWER_WATT, ENERGY_KILO_WATT_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant


ICON = "mdi:flash"

from .const import DOMAIN

from .energy_meter import EnergyMeter # This is the one that I have to make public eventually

import random

# This is taken from init
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> bool:
    """Set up pwrmicro from a config entry."""

#    hass.data.setdefault(DOMAIN, {})
#    # TODO 1. Create API instance
#    # TODO 2. Validate the API connection (and authentication)
#    # TODO 3. Store an API object for your platforms to access
#    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)
#
#    # TESTING
#    hass.data[DOMAIN][entry.entry_id] = 500
#
#    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    #async_add_entities([ConsumptionSensor(hass), GenerationSensor(hass)])
    async_add_entities([ConsumptionSensorPower(hass), GenerationSensorPower(hass), NetSensorPower(hass), GenerationSensorEnergy(hass), ConsumptionSensorEnergy(hass), NetSensorEnergy(hass)])

    return True

class W2SensorPower(SensorEntity):
    """Representation of a Sensor."""

    #_name = "Consumption"
    _unit_of_measurement = POWER_WATT
    _device_class = SensorDeviceClass.POWER
    _state_class = SensorStateClass.MEASUREMENT
    _state = None

    def __init__(self, hass):
        self._hass = hass
        self.energy_meter = EnergyMeter("192.168.1.19") # Get this from the config

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def state_class(self):
        """Return the state_class of the sensor."""
        return self._state_class

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    @property
    def state(self):
        """Icon to use in the frontend, if any."""
        return self._state

class W2SensorEnergy(SensorEntity):
    """Representation of a Sensor."""

    #_name = "Consumption"
    _unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _device_class = SensorDeviceClass.ENERGY
    _state_class = SensorStateClass.TOTAL
    _state = None

    def __init__(self, hass):
        self._hass = hass
        self.energy_meter = EnergyMeter("192.168.1.19") # Get this from the config

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def state_class(self):
        """Return the state_class of the sensor."""
        return self._state_class

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    @property
    def state(self):
        """Icon to use in the frontend, if any."""
        return self._state

class ConsumptionSensorPower(W2SensorPower):
    _name = "ConsumptionPower"

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        await self._hass.async_add_executor_job(self.energy_meter.refresh_data)
        self._state = self.energy_meter.consumption_power



class GenerationSensorPower(W2SensorPower):
    _name = "GenerationPower"

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        await self._hass.async_add_executor_job(self.energy_meter.refresh_data)
        if(self.energy_meter.generation_power):
            self._state = self.energy_meter.generation_power * -1 # -1 for display is nice

class NetSensorPower(W2SensorPower):
    _name = "NetPower"

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        await self._hass.async_add_executor_job(self.energy_meter.refresh_data)
        self._state = self.energy_meter.net_power 

# Note this is supposed to be GRID consumption
class ConsumptionSensorEnergy(W2SensorEnergy):
    _name = "ConsumptionEnergy"

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        await self._hass.async_add_executor_job(self.energy_meter.refresh_data)
        self._state = self.energy_meter.net_energy_imported

class GenerationSensorEnergy(W2SensorEnergy):
    _name = "GenerationEnergy"

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        await self._hass.async_add_executor_job(self.energy_meter.refresh_data)
        self._state = self.energy_meter.generation_energy

# Note this is return to grid
class NetSensorEnergy(W2SensorEnergy):
    _name = "NetEnergy"

    # Value back to the grid needs to be positive!
    # Might want to clamp to 0 when consuming. Not sure
    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        await self._hass.async_add_executor_job(self.energy_meter.refresh_data)
        self._state = self.energy_meter.net_energy_exported # This might be better in the main code. Not sure yet
