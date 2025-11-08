from query.services import get_services, Service
from pystemd.base import SDInterface
from json import dumps as json_dumps, JSONEncoder
from subprocess import call
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile

PRESETS: dict[str, callable[[Service], bool]] = {
    "down": lambda service: service.is_down(),
    "all": lambda service: True,
}

class BytesEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return o.decode('utf-8')
        else:
            try:
                return super().default(o)
            except TypeError:
                return None

def call_external(cmd: str, service: Service) -> bool:
    with NamedTemporaryFile() as temp_file:
        temp_file.write(json_dumps(service.asdict(), cls=BytesEncoder).encode("utf-8"))
        temp_file.flush()
        return call([cmd], shell=True, stdin=temp_file) == 0

def main():
    parser = ArgumentParser(description="Query systemd services")
    parser.add_argument("--preset", default="down", type=str, help="Preset to use for filtering services", choices=["all", "down"])
    parser.add_argument("--external", default="", type=str, help="External command to run for each service with a JSON input of the service data (exit 1 to ignore the service)")
    args = parser.parse_args()

    if args.external:
        print(f"Using external command: {args.external}")
        predicate = lambda service: call_external(args.external, service)
    else:
        print(f"Using preset: {args.preset}")
        predicate = PRESETS[args.preset]

    services = get_services()
    for service in services:
        if predicate(service):
            print(service)

if __name__ == "__main__":
    main()
