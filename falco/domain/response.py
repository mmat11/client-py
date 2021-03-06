import json
from datetime import datetime
from enum import Enum
from typing import Dict

from dateutil import tz

from falco.schema.output_pb2 import response
from falco.schema.schema_pb2 import priority, source
from falco.utils import pb_timestamp_from_datetime


class Response:
    __slots__ = (
        "time",
        "_priority",
        "_source",
        "rule",
        "output",
        "output_fields",
        "hostname",
    )

    class Priority(Enum):
        EMERGENCY = "emergency"
        ALERT = "alert"
        CRITICAL = "critical"
        ERROR = "error"
        WARNING = "warning"
        NOTICE = "notice"
        INFORMATIONAL = "informational"
        DEBUG = "debug"

    PB_PRIORITY_TO_PRIORITY_MAP = {
        0: Priority.EMERGENCY,
        1: Priority.ALERT,
        2: Priority.CRITICAL,
        3: Priority.ERROR,
        4: Priority.WARNING,
        5: Priority.NOTICE,
        6: Priority.INFORMATIONAL,
        7: Priority.DEBUG,
    }

    class Source(Enum):
        SYSCALL = "syscall"
        K8S_AUDIT = "k8s_audit"

    PB_SOURCE_TO_SOURCE_MAP = {
        0: Source.SYSCALL,
        1: Source.K8S_AUDIT,
    }

    SERIALIZERS = {"json": "to_json"}

    def __init__(
        self, time=None, priority=None, source=None, rule=None, output=None, output_fields=None, hostname=None,
    ):
        self.time: datetime = time.astimezone(tz.tzutc())
        self.priority: Response.Priority = priority
        self.source: Response.Source = source
        self.rule: str = rule
        self.output: str = output
        self.output_fields: Dict = output_fields
        self.hostname: str = hostname

    def __repr__(self):
        return f"{self.__class__.__name__}(time={self.time}, priority={self.priority}, source={self.source}, rule={self.rule}, output={self.output}, output_fields={self.output_fields}, hostname={self.hostname})"

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, p):
        self._priority = None
        if p and isinstance(p, Response.Priority):
            self._priority = p

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, s):
        self._source = None
        if s and isinstance(s, Response.Source):
            self._source = s

    @classmethod
    def from_proto(cls, pb_response):
        timestamp_dt = datetime.fromtimestamp(pb_response.time.seconds + pb_response.time.nanos / 1e9)

        return cls(
            time=timestamp_dt,
            priority=Response.PB_PRIORITY_TO_PRIORITY_MAP[pb_response.priority],
            source=Response.PB_SOURCE_TO_SOURCE_MAP[pb_response.source],
            rule=pb_response.rule,
            output=pb_response.output,
            output_fields=dict(pb_response.output_fields),
            hostname=pb_response.hostname,
        )

    def to_proto(self):
        return response(
            time=pb_timestamp_from_datetime(self.time),
            priority=priority.Value(self.priority.value),
            source=source.Value(self.source.value),
            rule=self.rule,
            output=self.output,
            output_fields=self.output_fields,
            hostname=self.hostname,
        )

    def to_json(self):
        return json.dumps(
            {
                "time": self.time.isoformat(),
                "priority": self.priority.value,
                "source": self.source.value,
                "rule": self.rule,
                "output": self.output,
                "output_fields": self.output_fields,
                "hostname": self.hostname,
            }
        )
