import requests

TOKEN="987f8b95a75b8dcc14926d98e708b07ed910102d"
API_URL="http://localhost:8000"

AUTH={"Authorization": f"Token {TOKEN}"}


def slugify(name):
    return name.lower().replace(" ", "-")


# 1. Site
site_ids = {}


def setupper(ids, url, pick_key, pick_value):
    r = requests.get(API_URL + url + "?limit=100000", headers=AUTH)
    out = r.json()
    if out["results"] is None:
        ids = {}
        return

    for result in out["results"]:
        ids[pick_key(result)] = pick_value(result)

def setup_site_ids():
    global site_ids
    r = requests.get(API_URL + "/api/dcim/sites/", headers=AUTH)
    out = r.json()
    if out["results"] is None:
        site_ids = {}
        return

    for result in out["results"]:
        site_ids[result["name"]] = result["id"]


def get_site_id(name, status):
    global site_ids
    ids = site_ids
    if name in ids:
        return ids[name]

    payload = {"name": name, "slug": slugify(name), "status": status}
    r = requests.post(API_URL + "/api/dcim/sites/", json=payload, headers=AUTH)
    out = r.json()
    site_id = out["id"]
    ids[name] = site_id

    return site_id

# 2. Manufacturer
manufacturer_ids = {}

setupper(manufacturer_ids, "/api/dcim/manufacturers/", lambda r: r["name"], lambda r: r["id"])

def setup_manufacturer_ids():
    global manufacturer_ids
    r = requests.get(API_URL + "/api/dcim/manufacturers/", headers=AUTH)
    out = r.json()
    if out["results"] is None:
        manufacturer_ids = {}
        return

    for result in out["results"]:
        manufacturer_ids[result["name"]] = result["id"]


def get_manufacturer_id(name):
    global manufacturer_ids
    if name in manufacturer_ids:
        return manufacturer_ids[name]

    payload = {"name": name, "slug": slugify(name)}
    r = requests.post(API_URL + "/api/dcim/manufacturers/", json=payload, headers=AUTH)
    out = r.json()
    manufacturer_id = out["id"]
    manufacturer_ids[name] = manufacturer_id

    return manufacturer_id


# 3. Device role
device_role_ids = {}


setupper(device_role_ids, "/api/dcim/device-roles/", lambda r: r["name"], lambda r: r["id"])

def setup_device_role_ids():
    global device_role_ids
    r = requests.get(API_URL + "/api/dcim/device-roles/", headers=AUTH)
    out = r.json()
    if out["results"] is None:
        device_role_ids = {}
        return

    for result in out["results"]:
        device_role_ids[result["name"]] = result["id"]


def get_device_role_id(name):
    global device_role_ids
    if name in device_role_ids:
        return device_role_ids[name]

    payload = {"name": name, "slug": slugify(name), "color": "333333"}
    r = requests.post(API_URL + "/api/dcim/device-roles/", json=payload, headers=AUTH)
    out = r.json()
    device_role_id = out["id"]
    device_role_ids[name] = device_role_id

    return device_role_id


# 4. Device type
device_type_ids = {}


setupper(device_type_ids, "/api/dcim/device-types/", lambda r: r["model"], lambda r: r["id"])

def setup_device_type_ids():
    global device_type_ids
    r = requests.get(API_URL + "/api/dcim/device-types/", headers=AUTH)
    out = r.json()
    if out["results"] is None:
        device_type_ids = {}
        return

    for result in out["results"]:
        device_type_ids[result["model"]] = result["id"]


def get_device_type_id(model, manufacturer):
    global device_type_ids
    if model in device_type_ids:
        return device_type_ids[model]

    payload = {"model": model, "slug": slugify(model), "manufacturer": manufacturer}
    r = requests.post(API_URL + "/api/dcim/device-types/", json=payload, headers=AUTH)
    out = r.json()
    device_type_id = out["id"]
    device_type_ids[model] = device_type_id

    return device_type_id


# 5. Device
device_ids = {}


def setup_device_ids():
    global device_ids
    r = requests.get(API_URL + "/api/dcim/devices/", headers=AUTH)
    out = r.json()
    if out["results"] is None:
        device_ids = {}
        return

    for result in out["results"]:
        device_ids[result["name"]] = result["id"]


def get_device_id(name, site, device_role, device_type):
    global device_ids
    if name in device_ids:
        return device_ids[name]

    payload = {"name": name, "site": site, "role": device_role, "device_type": device_type}
    r = requests.post(API_URL + "/api/dcim/devices/", json=payload, headers=AUTH)
    out = r.json()
    device_id = out["id"]
    device_ids[name] = device_id

    return device_id


# 6. Interface
interface_ids = {}


def setup_interface_ids():
    global interface_ids
    r = requests.get(API_URL + "/api/dcim/interfaces/", headers=AUTH)
    out = r.json()
    if out["results"] is None:
        interface_ids = {}
        return

    for result in out["results"]:
        interface_ids[result["device"]["id"]] = result["id"]


def get_interface_id(device_id):
    global interface_ids
    if device_id in interface_ids:
        return interface_ids[device_id]

    payload = {"device": device_id, "name": "Virtual", "type": "virtual"}
    r = requests.post(API_URL + "/api/dcim/interfaces/", json=payload, headers=AUTH)
    out = r.json()
    interface_id = out["id"]
    interface_ids[device_id] = interface_id

    return interface_id


# 7. vrfs
vrfs_ids = {}


def setup_vrfs_ids():
    global vrfs_ids
    r = requests.get(API_URL + "/api/ipam/vrfs/", headers=AUTH)
    out = r.json()
    if out["results"] is None:
        vrfs_ids = {}
        return

    for result in out["results"]:
        vrfs_ids[result["name"]] = result["id"]


setupper(device_ids, "/api/dcim/devices/", lambda r: r["name"], lambda r: r["id"])
setupper(site_ids, "/api/dcim/sites/", lambda r: r["name"], lambda r: r["id"])
setupper(interface_ids, "/api/dcim/interfaces/", lambda r: r["device"]["id"], lambda r: r["id"])


def get_vrfs_id(name):
    global vrfs_ids
    if name in vrfs_ids:
        return vrfs_ids[name]

    payload = {"name": name}
    r = requests.post(API_URL + "/api/ipam/vrfs/", json=payload, headers=AUTH)
    out = r.json()
    vrfs_id = out["id"]
    vrfs_ids[name] = vrfs_id

    return vrfs_id


# setup_site_ids()
# setup_manufacturer_ids()
# setup_device_role_ids()
# setup_device_type_ids()
# setup_device_ids()
# setup_interface_ids()
# setup_vrfs_ids()

device_id = get_device_id("Jeren reititin", get_site_id("Jeren koti", "active"), get_device_role_id("Router"), get_device_type_id("AC1750", get_manufacturer_id("tp-link")))

print(device_id)
interface_id = get_interface_id(device_id)
print(interface_id)

vrfs_id = get_vrfs_id("Jeren koti")
payload = {"address": f"192.168.0.1/32", "status": "active", "assigned_object_id": interface_id, "assigned_object_type": "dcim.interface", "vrf": vrfs_id}
r = requests.post(API_URL + "/api/ipam/ip-addresses/", json=payload, headers=AUTH)
print(r.status_code)
print(r.json())

# for i in range(255):
#     payload = {"address": f"192.168.0.{i}/32", "status": "active", "assigned_object_id": interface_id, "assigned_object_type": "dcim.interface"}
#     r = requests.post(API_URL + "/api/ipam/ip-addresses/", json=payload, headers=AUTH)

# print(device_ids)
