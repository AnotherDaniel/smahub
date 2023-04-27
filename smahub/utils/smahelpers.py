'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''

def unit_of_measurement(name):
    if (name.endswith("TmpVal")):
        return "°C"
    if (".W." in name):
        return "W"
    if (".TotWh" in name):
        return "Wh"
    if (".PvWh" in name):
        return "Wh"
    if (name.endswith(".TotW")):
        return "W"
    if (name.endswith(".TotW.Pv")):
        return "W"
    if (name.endswith(".Watt")):
        return "W"
    if (".A." in name):
        return "A"
    if (name.endswith(".Amp")):
        return "A"
    if (name.endswith(".Vol")):
        return "V"
    if (name.endswith(".VA.")):
        return "VA"
    if ("Tms" in name):
        return "ms"
    return ""

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False