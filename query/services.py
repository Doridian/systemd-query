from pystemd.systemd1 import Manager, Unit
from os.path import basename
from dataclasses import dataclass

IGNORE_STOPPED_SERVICE_TYPES = {b'dbus'}
IGNORE_TARGETS = {b'sleep.target', b'shutdown.target', b'timers.target'}

@dataclass(kw_only=True, frozen=True)
class Service:
    name: str
    unit: Unit

    @staticmethod
    def from_unit(unit_name: bytes) -> 'Service':
        unit = Unit(unit_name)
        unit.load()

        return Service(name=unit_name.removesuffix(b'.service'), unit=unit)
    
    def is_down(self) -> bool:
        # Ensure the service is loaded AND inactive first
        if self.unit.Unit.LoadState != b'loaded':
            return False
        if self.unit.Unit.ActiveState == b'active':
            return False
        # These means we don't care if the service is stopped, it is allowed to do that
        if self.unit.Service.Type in IGNORE_STOPPED_SERVICE_TYPES:
            return False
        wantedBy = set([w.strip() for w in self.unit.Unit.WantedBy])
        if not (wantedBy - IGNORE_TARGETS):
            return False
        if self.unit.Service.Type == b'oneshot' and self.unit.Service.RemainAfterExit != b'yes':
            return False

        return True

    def __repr__(self):
        return f"Service(unit={self.name}, active={self.unit.Unit.ActiveState}, load={self.unit.Unit.LoadState}, sub={self.unit.Unit.SubState})"

def get_services() -> list[Service]:
    manager = Manager()
    manager.load()
    units = manager.Manager.ListUnitFiles()
    return [Service.from_unit(basename(unit[0])) for unit in units if unit[0].endswith(b'.service') and not unit[0].endswith(b'@.service') and unit[1] == b'enabled']
