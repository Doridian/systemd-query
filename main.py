from query.services import get_services

def main():
    services = get_services()
    for service in services:
        if service.is_down():
            print(service)

if __name__ == "__main__":
    main()
