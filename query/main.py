from query.services import get_services, Service
from argparse import ArgumentParser

PRESETS: dict[str, callable] = {
    "down": lambda service: service.is_down(),
    "all": lambda service: True,
}

def main():
    parser = ArgumentParser(description="Query systemd services")
    parser.add_argument("--preset", default="down", type=str, help="Preset to use for filtering services", choices=["all", "down"])
    args = parser.parse_args()

    predicate = PRESETS[args.preset]

    print(f"Using preset: {args.preset}")

    services = get_services()
    for service in services:
        if predicate(service):
            print(service)

if __name__ == "__main__":
    main()
