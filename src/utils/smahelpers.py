'''
This code is adapted from https://github.com/littleyoda/Home-Assistant-Tripower-X-MQTT
Thank you littleyoda!
'''

# Lookup table, gathered by downloading TriPower X current values as CSV file and then doing conversions to a python dict
# Contents: Channel: Group, Name Unit
TRIPOWER_PARAM_DICT = {
    'Coolsys.Inverter.TmpVal[0]': ('Device', 'Inverter temperature [1]', '°C'),
    'Coolsys.Inverter.TmpVal[1]': ('Device', 'Inverter temperature [2]', '°C'),
    'Coolsys.Inverter.TmpVal[2]': ('Device', 'Inverter temperature [3]', '°C'),
    'DcMs.Amp[0]': ('DC Side', 'DC current input [A]', 'A'),
    'DcMs.Amp[1]': ('DC Side', 'DC current input [B]', 'A'),
    'DcMs.Amp[2]': ('DC Side', 'DC current input [C]', 'A'),
    'DcMs.Vol[0]': ('DC Side', 'DC voltage input [A]', 'V'),
    'DcMs.Vol[1]': ('DC Side', 'DC voltage input [B]', 'V'),
    'DcMs.Vol[2]': ('DC Side', 'DC voltage input [C]', 'V'),
    'DcMs.Watt[0]': ('DC Side', 'DC power input [A]', 'W'),
    'DcMs.Watt[1]': ('DC Side', 'DC power input [B]', 'W'),
    'DcMs.Watt[2]': ('DC Side', 'DC power input [C]', 'W'),
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
    'Setpoint.PlantControl.Inverter.WModCfg.WCtlComCfg.W': ('System and device control', 'Active power limitation by PV system control', 'W')
}


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
