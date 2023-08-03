'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''

# Lookup table, gathered by downloading TriPower X current values as CSV file and then doing conversions to a python dict
# Contents: Channel: Group, Name Unit
TRIPOWER_PARAM_DICT = {
    'Coolsys.Inverter.TmpVal': ('Device', 'Inverter temperature [3]', '°C'),
    'DcMs.Amp': ('DC Side', 'DC current input [C]', 'A'),
    'DcMs.Vol': ('DC Side', 'DC voltage input [C]', 'V'),
    'DcMs.Watt': ('DC Side', 'DC power input [C]', 'W'),
    'GridGuard.Cntry': ('Grid Monitoring', 'Country standard set', ''),
    'GridMs.A.phsA': ('AC Side', 'Grid current phase L1', 'A'),
    'GridMs.A.phsB': ('AC Side', 'Grid current phase L2', 'A'),
    'GridMs.A.phsC': ('AC Side', 'Grid current phase L3', 'A'),
    'GridMs.Hz': ('AC Side', 'Grid frequency', 'Hz'),
    'GridMs.PhV.phsA': ('AC Side', 'Grid voltage phase L1', 'V'),
    'GridMs.PhV.phsA2B': ('AC Side', 'Grid voltage phase L1 against L2', 'V'),
    'GridMs.PhV.phsB': ('AC Side', 'Grid voltage phase L2', 'V'),
    'GridMs.PhV.phsB2C': ('AC Side', 'Grid voltage phase L2 against L3', 'V'),
    'GridMs.PhV.phsC': ('AC Side', 'Grid voltage phase L3', 'V'),
    'GridMs.PhV.phsC2A': ('AC Side', 'Grid voltage phase L3 against L1', 'V'),
    'GridMs.TotA': ('AC Side', 'Grid current', 'A'),
    'GridMs.TotPFEEI': ('AC Side', 'EEI displacement power factor', ''),
    'GridMs.TotPFExt': ('AC Side', 'Excitation type of cos φ', ''),
    'GridMs.TotPFPrc': ('AC Side', 'Displacement power factor', ''),
    'GridMs.TotVA': ('AC Side', 'Apparent power', 'VA'),
    'GridMs.TotVAr': ('AC Side', 'Reactive power', 'var'),
    'GridMs.TotW': ('AC Side', 'Power', 'W'),
    'GridMs.TotW.Pv': ('AC Side', 'Power', 'W'),
    'GridMs.VA.phsA': ('AC Side', 'Apparent power L1', 'VA'),
    'GridMs.VA.phsB': ('AC Side', 'Apparent power L2', 'VA'),
    'GridMs.VA.phsC': ('AC Side', 'Apparent power L3', 'VA'),
    'GridMs.VAr.phsA': ('AC Side', 'Reactive power L1', 'var'),
    'GridMs.VAr.phsB': ('AC Side', 'Reactive power L2', 'var'),
    'GridMs.VAr.phsC': ('AC Side', 'Reactive power L3', 'var'),
    'GridMs.W.phsA': ('AC Side', 'Power L1', 'W'),
    'GridMs.W.phsB': ('AC Side', 'Power L2', 'W'),
    'GridMs.W.phsC': ('AC Side', 'Power L3', 'W'),
    'InOut.GI1': ('Further Applications', 'Digital group input', ''),
    'Inverter.VArModCfg.PFCtlVolCfg.Stt': ('System and device control', 'cos φ(V), status', ''),
    'Isolation.FltA': ('DC Side', 'Residual current', 'A'),
    'Isolation.LeakRis': ('DC Side', 'Insulation resistance', 'kOhm'),
    'Metering.TotFeedTms': ('AC Side', 'Feed-in time', 's'),
    'Metering.TotOpTms': ('AC Side', 'Operating time', 's'),
    'Metering.TotWhOut': ('AC Side', 'Total yield', 'kWh'),
    'Metering.TotWhOut.Pv': ('AC Side', 'Total yield', 'kWh'),
    'Operation.BckStt': ('Device', 'Backup mode status', ''),
    'Operation.DrtStt': ('Status', 'Reason for derating', ''),
    'Operation.Evt.Dsc': ('Status', 'Fault correction measure', ''),
    'Operation.Evt.Msg': ('Status', 'Message', ''),
    'Operation.EvtCntIstl': ('Status', 'Number of events for installer', ''),
    'Operation.EvtCntUsr': ('Status', 'Number of events for user', ''),
    'Operation.GriSwCnt': ('AC Side', 'Number of grid connections', ''),
    'Operation.GriSwStt': ('Status', 'Grid relay/contactor', ''),
    'Operation.Health': ('Status', 'Condition', ''),
    'Operation.HealthStt.Alm': ('Status', 'Nominal power in Fault Mode', 'W'),
    'Operation.HealthStt.Ok': ('Status', 'Nominal power in Ok Mode', 'kW'),
    'Operation.HealthStt.Wrn': ('Status', 'Nominal power in Warning Mode', 'W'),
    'Operation.OpStt': ('Status', 'General operating status', ''),
    'Operation.PvGriConn': ('AC Side', 'Plant mains connection', ''),
    'Operation.RstrLokStt': ('Status', 'Block status', ''),
    'Operation.RunStt': ('Status', 'Operating status', ''),
    'Operation.StandbyStt': ('Status', 'Standby status', ''),
    'Operation.VArCtl.VArModAct': ('System and device control', 'Active reactive power range', ''),
    'Operation.VArCtl.VArModStt': ('System and device control', 'Active reactive power behavior', ''),
    'Operation.WMaxLimSrc': ('System and device control', 'Source of maximum active power setpoint', ''),
    'Operation.WMinLimSrc': ('System and device control', 'Source of minimum active power setpoint', ''),
    'PvGen.PvW': ('AC Side', 'PV generation power', 'W'),
    'PvGen.PvWh': ('AC Side', 'Meter count and PV gen. meter', 'kWh'),
    'SunSpecSig.SunSpecTx': ('DC Side', 'SunSpec life sign', ''),
    'Upd.Stt': ('Status', 'Status of the firmware update', ''),
    'WebConn.Stt': ('External Communication', 'Status of the Webconnect functionality', ''),
    'Wl.ConnStt': ('System communication', 'Wi-Fi connection status', ''),
    'Wl.SigPwr': ('System communication', 'Signal strength of the selected network', '%'),
    'Setpoint.PlantControl.InOut.DigOut': ('Device', 'Digital output', ''),
    'Setpoint.PlantControl.Inverter.WModCfg.WCtlComCfg.W': ('System and device control', 'Active power limitation by PV system control', 'W'),
    'SunSpecSig.SunSpecTx.1': ('DC Side', 'SunSpec life sign [1]', ''),
    'Wl.AcqStt': ('System communication', 'Status of Wi-Fi scan', ''),
    'Wl.SoftAcsConnStt': ('System communication', 'Soft Access Point status', ''),
}

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
    
def parameter_unit(name):
    if name in TRIPOWER_PARAM_DICT:
        return TRIPOWER_PARAM_DICT[name][2]
    else:
        return ""


def parameter_description(name):
    if name in TRIPOWER_PARAM_DICT:
        return TRIPOWER_PARAM_DICT[name][1]
    else:
        return ""


def parameter_group(name):
    if name in TRIPOWER_PARAM_DICT:
        return TRIPOWER_PARAM_DICT[name][0]
    else:
        return ""


def unit_of_measurement(name):
    if name.endswith("TmpVal"):
        return "°C"
    if ".W." in name or name.endswith("W"):
        return "W"
    if ".TotWh" in name:
        return "Wh"
    if ".PvWh" in name:
        return "Wh"
    if name.endswith(".TotW"):
        return "W"
    if name.endswith(".TotW.Pv"):
        return "W"
    if name.endswith(".Watt"):
        return "W"
    if ".A." in name:
        return "A"
    if name.endswith(".Amp"):
        return "A"
    if name.endswith(".Vol"):
        return "V"
    if ".VA." in name or name.endswith(".VA"):
        return "VA"
    if ".VAr." in name or name.endswith(".VAr"):
        return "VAr"
    if "Tms" in name:
        return "ms"
    return ""


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
