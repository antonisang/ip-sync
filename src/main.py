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


def get_records(domain: str) -> list[dict[str, str | int | None]]:
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
    # Handle the case where the domain name is not defined on Digital Ocean
    if target_record.status_code == 404:
        print(f"The domain {domain} could not be found in Digital Ocean")
        exit(1)
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


def get_filtered_records(domains: list[str], exceptions: dict[str, list[str]]) -> dict[str, list[str]]:
    """
    Obtains all the A-type records of each domain, filters them against the exceptions dictionary and returns a new
    dictionary containing the domain as a key and each allowed subdomain ID in a list of strings as values
    :param domains: A list of domains as strings to obtain records from
    :param exceptions: A dictionary using the domain as a key and the subdomains to exclude as a list of strings
    :return: A dictionary with all the domains as keys and subdomain IDs as a list of strings as values
    """
    filtered_records = dict()
    for domain in domains:
        domain_records = get_records(domain)
        if len(domain_records) > 0:
            filtered_domain_records = [d for d in domain_records if d["name"] not in exceptions[domain]]
            filtered_records[domain] = [d["id"] for d in filtered_domain_records]
            # All subdomains are included in the exceptions
            if len(filtered_records[domain]) == 0:
                print(f"All subdomains for {domain} have been excluded. Please consider removing the {domain} "
                      f"from the domains array or remove some of its exceptions")
                exit(1)
    return filtered_records


current_time = datetime.datetime.now()
record_ids = get_filtered_records(CONFIG.domains, CONFIG.exceptions)

# Driver code
while True:
    if current_time + datetime.timedelta(hours=1) < datetime.datetime.now():
        record_ids = get_filtered_records(CONFIG.domains, CONFIG.exceptions)
        current_time = datetime.datetime.now()
    time.sleep(180)
    new_ip = get_current_ip()
    if new_ip != get_record_ip(record_ids[0]):
        for record_id in record_ids:
            requests.patch(f"https://api.digitalocean.com/v2/domains/{DOMAIN}/records/{record_id}",
                           json={"type": "A", "data": f"{new_ip}"},
                           headers={"Authorization": f"Bearer {API_KEY}"})
            time.sleep(5)
        last_ip = new_ip
