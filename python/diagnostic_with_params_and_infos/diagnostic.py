import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from random import choice, choices, random, uniform
from time import time
from typing import Literal, Optional

from common import publish_message
from custom_service import CustomService
from nats.aio import client

BASE_NAME_ROOT = "urn:cpt:device:sn"
DEVICE_SERIAL_NUMBER = os.environ.get("DEVICE_SERIAL_NUMBER", "1122334455")
MAX_DATA_VALUE = 500


VARIABLE_NAMES_AND_UNITS = [
    ("temperature", "C"),
    ("voltage", "V"),
    ("current_flow", "A"),
    ("power_factor", "cos phi"),
    ("frequency", "Hz"),
    ("humidity", "%"),
    ("pressure", "Pa"),
    ("flow_rate", "m/s^3"),
    ("energy", "kWh"),
    ("efficiency", "%"),
    ("load_factor", "%"),
    ("phase_angle", "degree"),
    ("resistance", "ohm"),
    ("reactance", "ohm"),
    ("impedance", "ohm"),
    ("power", "W"),
    ("capacity", "F"),
    ("torque", "Nm"),
    ("speed", "m/s"),
    ("acceleration", "m/s^2"),
]


logger = logging.getLogger("diagnostic")


def to_camel_case(snake_str: str) -> str:
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def to_lower_camel_case(snake_str: str) -> str:
    return snake_str[0].lower() + to_camel_case(snake_str)[1:]


class BaseEnum(Enum):
    def __str__(self):
        return str(self.name)


class MetricDataType(int, BaseEnum):
    STRING = 0
    NUMBER = 1
    BOOLEAN = 2


class MetricType(int, BaseEnum):
    TEMPORAL = 0
    INCREMENTAL = 1


class MetricGranularity(str, BaseEnum):
    SECOND = "s"
    MINUTE = "m"
    HOUR = "h"
    DAY = "d"
    WEEK = "w"
    MONTH = "M"
    YEAR = "y"


class DeviceStatus(str, BaseEnum):
    # Connected and disconnected are also sent on mqtt conenction by the REDIS service
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UPDATING = "updating"


@dataclass
class DeviceMetric:
    id: str
    name: str
    unit: str
    type: MetricType
    data_type: MetricDataType
    # int + MetricGranularity
    min_granularity: Optional[str] = None
    label: Optional[str] = None

    _min: float = 0
    _max: float = MAX_DATA_VALUE
    _last_data_sent: float = 0

    @staticmethod
    def custom_dict(kv_pairs):
        return {to_lower_camel_case(k): v for k, v in kv_pairs if not k.startswith("_")}

    @staticmethod
    def get_random():
        id = str(uuid.uuid4().fields[-1])
        type = MetricType.INCREMENTAL if random() > 0.5 else MetricType.TEMPORAL
        name, unit = choice(VARIABLE_NAMES_AND_UNITS)
        _max = uniform(0, MAX_DATA_VALUE)

        return DeviceMetric(
            id=id,
            name=name,
            unit=unit,
            type=type,
            data_type=MetricDataType.NUMBER,
            _min=0,
            _max=_max,
        )

    def to_urn(self) -> str:
        return f"{get_bn()}{self.id}"

    def as_dict(self) -> dict:
        return asdict(self, dict_factory=self.custom_dict)

    def get_random_data_value(self) -> float:
        random_value = round(uniform(self._min, self._max), 3)

        new_value = (
            random_value
            if self.type == MetricType.TEMPORAL
            else random_value / 10 + self._last_data_sent
        )

        self._last_data_sent = new_value

        return new_value


def get_bn() -> str:
    return f"{BASE_NAME_ROOT}:{DEVICE_SERIAL_NUMBER}:"


def get_random_metrics(n: int) -> list[DeviceMetric]:
    return [DeviceMetric.get_random() for _ in range(n)]


def get_random_status() -> DeviceStatus:
    return choices(
        [DeviceStatus.CONNECTED, DeviceStatus.DISCONNECTED, DeviceStatus.UPDATING],
        weights=[0.5, 0.5, 0.1],
        k=1,
    )[0]


def _build_info_message() -> dict:
    return {
        "fwVersion": "1.0.0",
        "status": get_random_status().value,
        "timestamp": round(time()),
    }


def _build_params_message(metrics: list[DeviceMetric]) -> dict:
    return {
        "bn": get_bn(),
        "n": "metrics",
        "vs": json.dumps([v.as_dict() for v in metrics]),
    }


def _build_data_message(metric: DeviceMetric) -> dict:
    return {
        "t": time(),
        "n": metric.to_urn(),
        "v": metric.get_random_data_value(),
        "u": metric.unit,
    }


class DiagnosticService(CustomService):
    service_name = "diagnostic"

    def __init__(self, nc: client.Client, update_loop_interval_ms=60_000) -> None:
        super().__init__(nc, update_loop_interval_ms)

        self._last_infos_msg_ts: float = 0
        self._infos_msg_interval_s = 10 * 60

        self._last_params_msg_ts: float = 0
        self._params_msg_interval_s = 10 * 60

        self._metrics = get_random_metrics(10)

    def _get_message_topic(self) -> Literal["infos", "data", "params"]:
        if (time() - self._last_infos_msg_ts) > self._infos_msg_interval_s:
            self._last_infos_msg_ts = time()
            return "infos"

        if (time() - self._last_params_msg_ts) > self._params_msg_interval_s:
            self._last_params_msg_ts = time()
            return "params"

        return "data"

    async def _send_message(self, topic: str = "data") -> None:
        # Override input topic
        topic = self._get_message_topic()

        message = self._build_message(topic)
        if not message:
            return
        logger.debug(f"Publishing {self.service_name} message: {message}")

        await publish_message(self._nc, topic, message)

    def _build_message(self, topic: str, **kwargs) -> dict | None:
        match topic:
            case "infos":
                return _build_info_message()
            case "params":
                return _build_params_message(self._metrics)
            case "data":
                return _build_data_message(choice(self._metrics))
