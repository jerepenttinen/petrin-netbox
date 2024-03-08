import requests
import argparse

# Mitä pitää tehdä vielä:
# 1. CSV parsinta

parser = argparse.ArgumentParser()
parser.add_argument("--token", dest="token", type=str, help="Netbox API token", required=True)
parser.add_argument("--debug", dest="debug", type=bool, help="Enable debug printing", required=False, default=False)
# parser.add_argument( "--api", dest="api", type=str, help="Netbox API URL", required=True)
# parser.add_argument( "--file", dest="file", type=str, help="Input CSV file path", required=True)
args = parser.parse_args()

TOKEN=args.token
API_URL="http://localhost:8000"

AUTH={"Authorization": f"Token {TOKEN}"}
DEBUG=args.debug

def slugify(name):
    return name.lower().replace(" ", "-")


# 1. Site
site_ids = {}
manufacturer_ids = {}
device_role_ids = {}
device_type_ids = {}
device_ids = {}
interface_ids = {}
vrfs_ids = {}


def get_device_type_key(manufacturer, model):
    return f'{manufacturer}-{model}'


def setupper(ids, url, pick_key, pick_value):
    full_url = API_URL + url + "?limit=100000"
    r = requests.get(full_url, headers=AUTH)
    out = r.json()
    if DEBUG:
        print("GET", full_url, r.status_code, out)

    if out["results"] is None:
        return

    for result in out["results"]:
        ids[pick_key(result)] = pick_value(result)


setupper(manufacturer_ids, "/api/dcim/manufacturers/", lambda r: r["name"], lambda r: r["id"])
setupper(device_role_ids, "/api/dcim/device-roles/", lambda r: r["name"], lambda r: r["id"])
setupper(device_type_ids, "/api/dcim/device-types/", lambda r: get_device_type_key(r["manufacturer"]["id"], r["model"]), lambda r: r["id"])
setupper(device_ids, "/api/dcim/devices/", lambda r: r["name"], lambda r: r["id"])
setupper(site_ids, "/api/dcim/sites/", lambda r: r["name"], lambda r: r["id"])
setupper(interface_ids, "/api/dcim/interfaces/", lambda r: r["device"]["id"], lambda r: r["id"])
setupper(vrfs_ids, "/api/ipam/vrfs/", lambda r: r["name"], lambda r: r["id"])


def getter(ids, key, url, payload):
    full_url = API_URL + url
    if key in ids:
        if DEBUG:
            print("GET", full_url, key, "cached", ids[key])
        return ids[key]

    r = requests.post(API_URL + url, json=payload, headers=AUTH)
    out = r.json()
    if DEBUG:
        print("GET", full_url, key, r.status_code, out)
    ids[key] = out["id"]

    return out["id"]


def get_site_id(name, status):
    global site_ids
    return getter(site_ids, name, "/api/dcim/sites/", {"name": name, "slug": slugify(name), "status": status})


def get_manufacturer_id(name):
    global manufacturer_ids
    return getter(manufacturer_ids, name, "/api/dcim/manufacturers/", {"name": name, "slug": slugify(name)})


# 3. Device role
def get_device_role_id(name):
    global device_role_ids
    return getter(device_role_ids, name, "/api/dcim/device-roles/", {"name": name, "slug": slugify(name), "color": "333333"})


# 4. Device type
def get_device_type_id(model, manufacturer):
    global device_type_ids
    return getter(device_type_ids, get_device_type_key(manufacturer, model), "/api/dcim/device-types/", {"model": model, "slug": slugify(model), "manufacturer": manufacturer})


# 5. Device
def get_device_id(name, site, device_role, device_type):
    global device_ids
    return getter(device_ids, name, "/api/dcim/devices/", {"name": name, "site": site, "role": device_role, "device_type": device_type})


# 6. Interface
def get_interface_id(device_id):
    global interface_ids
    return getter(interface_ids, device_id, "/api/dcim/interfaces/", {"device": device_id, "name": "Virtual", "type": "virtual"})


# 7. vrfs
def get_vrfs_id(name):
    global vrfs_ids
    return getter(vrfs_ids, name, "/api/ipam/vrfs/", {"name": name})


def put_ip_address(ip_address, vrf_id, interface_id, status):
    payload = {"address": ip_address, "status": status, "assigned_object_id": interface_id, "assigned_object_type": "dcim.interface", "vrf": vrf_id}
    requests.post(API_URL + "/api/ipam/ip-addresses/", json=payload, headers=AUTH)


csv = [
    # site  status    name       ip_address                        device_type   manufactur   role
    ["S01", "Active", "device1", ["10.10.10.1/24", "10.10.10.2/24"], "router2000", "Cisco", "Switch"],
    ["S02", "Active", "device2", ["10.10.10.1/24", "10.10.10.2/24"], "router2000", "Tampereen Infra Oy", "Switch"],
]


for row in csv:
    r = {
        "site": row[0],
        "status": row[1],
        "name": row[2],
        "ip_address": row[3],
        "device_type": row[4],
        "manufacturer": row[5],
        "role": row[6],
    }

    device_id = get_device_id(r["name"], get_site_id(r["site"], r["status"].lower()), get_device_role_id(r["role"]), get_device_type_id(r["device_type"], get_manufacturer_id(r["manufacturer"])))
    interface_id = get_interface_id(device_id)

    for ip in r["ip_address"]:
        put_ip_address(ip, get_vrfs_id(r["site"]), interface_id, r["status"].lower())
