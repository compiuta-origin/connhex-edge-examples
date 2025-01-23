from random import randrange
from time import time

from custom_service import CustomService


class DiagnosticService(CustomService):
    service_name = "diagnostic"

    # Implement your own logic to get current values.
    def _get_battery_charge(self) -> int:
        return randrange(0, 101)

    # Implement your own logic to get current values.
    def _get_fuel_level(self) -> int:
        return randrange(0, 101)

    def _build_message(self):
        base_name = f"urn:cpt:{self.service_name}"
        now = time()
        return [
            {
                "t": now,
                "n": f"{base_name}:battery-charge",
                "u": "%EL",
                "v": self._get_battery_charge(),
            },
            {
                "t": now,
                "n": f"{base_name}:fuel-level",
                "u": "%FL",
                "v": self._get_fuel_level(),
            },
        ]
