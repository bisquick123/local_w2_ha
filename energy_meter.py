import requests
import json
import time

SECONDS_PER_HOUR = 3600
WATTS_PER_KILOWATT = 1000


# GLOBAL_CACHE = ( {}, 0 )
class EnergyMeter:
    # ip = None
    # consumption_power = None
    # generation_power = None
    # net_power = None
    # generation_energy = None
    # consumption_energy = None
    # net_energy = None
    # net_energy_exported = None
    # net_energy_imported = None

    def __init__(self, ip):
        self.ip = ip
        self.consumption_power = None
        self.generation_power = None
        self.net_power = None
        self.generation_energy = None
        self.consumption_energy = None
        self.net_energy = None
        self.net_energy_exported = None
        self.net_energy_imported = None
        self.submeter_power = None
        self.submeter_energy = None

    def _get_raw_data(self):
        try:
            return requests.get(f"http://{self.ip}/current-sample").text
        except Exception as e:
            print(e)
            return "{}"

    def refresh_data(self):
        # global GLOBAL_CACHE
        # if( (time.time() - GLOBAL_CACHE[1]) < 30 ):
        #    print("Using cache")
        #    energy_dict = GLOBAL_CACHE[0]
        # else:
        #    print("Not Using cache")
        #    raw_json = self._get_raw_data()
        #    energy_dict = json.loads(raw_json)
        #    GLOBAL_CACHE = ( energy_dict, time.time() )
        raw_json = self._get_raw_data()
        energy_dict = json.loads(raw_json)
        if energy_dict:
            channel_list = energy_dict["channels"]
            self._fill_data(channel_list)

    def _fill_data(self, channel_list):
        for channel in channel_list:
            channel_type = channel["type"]
            power = float(channel["p_W"])
            imported_energy = to_kilowatt_hours(channel["eImp_Ws"])
            exported_energy = to_kilowatt_hours(channel["eExp_Ws"])

            if channel_type == "GENERATION":
                self.generation_power = power
                self.generation_energy = exported_energy
            elif channel_type == "NET":
                self.net_power = power
                self.net_energy_exported = exported_energy
                self.net_energy_imported = imported_energy
            elif channel_type == "CONSUMPTION":
                self.consumption_power = power
                self.consumption_energy = imported_energy
            elif channel_type == "SUBMETER":
                self.submeter_power = power
                self.submeter_energy = imported_energy
        self._calculate_missing()

    def _calculate_missing(self):
        """Calculate missing channel. Note: Generation is negative"""
        # Not sure why this stopped working
        # As a note for the future:
        # if not consumption_power is not executing. But if you pass it all the way through it is None  in the async_update
        # if not self.consumption_power:
        #    if self.generation_power and self.net_power:
        #        self.consumption_power = self.net_power - self.generation_power
        #        self.consumption_energy = self.generation_energy - (self.net_energy_exported - self.net_energy_imported)

        if (
            self.generation_power and self.net_power
        ):  # Making an assumption it is there for testing purposes
            self.consumption_power = self.net_power - self.generation_power
            self.consumption_energy = self.generation_energy - (
                self.net_energy_exported - self.net_energy_imported
            )

        if not self.net_power:
            if self.generation_power and self.consumption_power:
                self.net_power = self.generation_power + self.consumption_power


def to_kilowatt_hours(watt_seconds):
    return watt_seconds / (SECONDS_PER_HOUR * WATTS_PER_KILOWATT)
