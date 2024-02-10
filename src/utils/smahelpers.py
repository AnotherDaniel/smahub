'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''

# Lookup for various status texts used by TripowerX inverter parameters
# Not complete by a long shot I guess, needs to be extended as I see more values in my system
TRIPOWER_STATUS_DICT = {
    302: "---",
    937: "---",
    973: "---",
    303: "Off",
    307: "Ok",
    311: "Open",
    3366: "No scan completed",
    1130: "No",
    1295: "Standby",
    295: "MPP",
    569: "Activated",
    1779: "Separated",
    1780: "Public electricity mains",
    27: "Special setting",
    51: "Closed",
    884: "not active",
    1440: "Grid mode",
    1042: "Underexcited",
    4570: "Wait for enable operation",
    16777213: "Information not available",
}


def status_string(id):
    if id in TRIPOWER_STATUS_DICT:
        return TRIPOWER_STATUS_DICT[id]
    else:
        return ""


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
