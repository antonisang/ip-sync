import sys
import time
import datetime
import requests


# Parse script config
try:
    DOMAIN = sys.argv[1]
    API_KEY = sys.argv[2]
except Exception:
    exit(1)


def get_current_ip():
    return requests.get("https://api.ipify.org").text


def get_records_ids():
    target_record = requests.get(f"https://api.digitalocean.com/v2/domains/{DOMAIN}/records", 
                             params={"type": "A", "per_page": 200},
                             headers={"Authorization": f"Bearer {API_KEY}"})
    json_result = target_record.json()
    id_list = [x["id"] for x in json_result["domain_records"]]
    return id_list


def get_record_ip(record_id):
    record_data = requests.get(f"https://api.digitalocean.com/v2/domains/{DOMAIN}/records/{record_id}", 
                             headers={"Authorization": f"Bearer {API_KEY}"})
    json_data = record_data.json()
    return json_data['domain_record']['data']
    

# Load last IP from file
try:
    with open("./last_ip.txt", "r") as f:
        last_ip = f.read()
except Exception:
    with open("./last_ip.txt", "w") as f:
        obtained_ip = get_current_ip()
        f.write(obtained_ip)
        last_ip = obtained_ip


current_time = datetime.datetime.now()
record_ids = get_records_ids()


# Driver code
while True:
    if current_time + datetime.timedelta(hours=1) < datetime.datetime.now():
        record_ids = get_records_ids()
        current_time = datetime.datetime.now()
    time.sleep(20)
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

        