import time
import datetime
import requests
from schema import Config

# Load script config
try:
    CONFIG = Config("./config.json")
except Exception as e:
    print(e)
    exit(1)


def get_current_ip() -> str:
    """
    Returns the current external IPv4 address of the system
    :return: An IPv4 address as a string
    """
    return requests.get("https://api.ipify.org").text


def get_records_ids(domain: str) -> list[dict[str, str | int | None]]:
    """
    Returns a list of all A-type records. Each record is a dictionary with the following format::

        {
            'data': '177.48.59.2',
            'flags': None,
            'id': 0123456789,
            'name': 'sales',
            'port': None,
            'priority': None,
            'tag': None,
            'ttl': 3600,
            'type': 'A',
            'weight': None,
        }

    :param domain: The domain to get records for
    :returns: A list of dictionaries containing data about the domain records
    """
    target_record = requests.get(f"https://api.digitalocean.com/v2/domains/{domain}/records",
                                 params={"type": "A", "per_page": 200},
                                 headers={"Authorization": f"Bearer {CONFIG.api_key}"})
    json_result = target_record.json()["domain_records"]
    return json_result


def get_record_ip(subdomain_domain: str, subdomain_id: str) -> str:
    """
    Returns the IPv4 address of the specified subdomain by the function arguments
    :param subdomain_domain: The domain name that the desired record is in
    :param subdomain_id: The subdomain record ID to get the IPv4 address for
    :return:
    """
    record_data = requests.get(f"https://api.digitalocean.com/v2/domains/{subdomain_domain}/records/{subdomain_id}",
                               headers={"Authorization": f"Bearer {CONFIG.api_key}"})
    json_data = record_data.json()
    return json_data['domain_record']['data']


# Load last IP from file
try:
    with open("./last_ip.txt", "r") as f:
        last_ip = f.read()
except FileNotFoundError:
    with open("./last_ip.txt", "w") as f:
        obtained_ip = get_current_ip()
        f.write(obtained_ip)
        last_ip = obtained_ip
except Exception as e:
    print(f"Unexpected error: {e}\n")
    exit(1)

current_time = datetime.datetime.now()
record_ids = get_records_ids()

# Driver code
while True:
    if current_time + datetime.timedelta(hours=1) < datetime.datetime.now():
        record_ids = get_records_ids()
        current_time = datetime.datetime.now()
    time.sleep(180)
    new_ip = get_current_ip()
    if (last_ip != new_ip) or (new_ip != get_record_ip(record_ids[0])):
        with open("./last_ip.txt", "w") as f:
            f.write(new_ip)
        for record_id in record_ids:
            requests.patch(f"https://api.digitalocean.com/v2/domains/{DOMAIN}/records/{record_id}",
                           json={"type": "A", "data": f"{new_ip}"},
                           headers={"Authorization": f"Bearer {API_KEY}"})
            time.sleep(5)
        last_ip = new_ip
