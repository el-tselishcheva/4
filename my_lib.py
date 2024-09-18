import struct, pytz, datetime
from pysnmp.hlapi import *

class StorageInfo:
    def __init__(self, desc, used, size):
        self.desc = desc
        self.used = used
        self.size = size

def get_storage_info(community_str, ip):
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community_str),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.25.2.3.1.3')),   # hrStorageDescr
        ObjectType(ObjectIdentity('1.3.6.1.2.1.25.2.3.1.4')),   # hrStorageAllocationUnits
        ObjectType(ObjectIdentity('1.3.6.1.2.1.25.2.3.1.5')),   # hrStorageSize
        ObjectType(ObjectIdentity('1.3.6.1.2.1.25.2.3.1.6')),   # hrStorageUsed
        lexicographicMode = False
    )

    storages = []
    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            size = int(varBinds[1][1]) * int(varBinds[2][1]) / (1024**3)
            used = int(varBinds[1][1]) * int(varBinds[3][1]) / (1024**3)
            storages.append(StorageInfo(varBinds[0][1], round(used, 1), round(size, 1)))

    return storages

def get_processes(community_str, ip):
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community_str),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.25.1.6')),   # hrSystemProcesses
        lexicographicMode = False
    )

    res_str = ''
    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                res_str = str(varBind[1])

    return res_str

def get_sys_up_time(community_str, ip):
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community_str),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3')),  # sysUpTime
        lexicographicMode = False
    )

    res_str = ''
    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                ticks = int(varBind[1])

    res_str = str(datetime.timedelta(seconds = ticks / 100))
    return res_str

def calc_cpu_usage(community_str, ip):
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community_str),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.25.3.3.1.2')),   # hrProcessorLoad
        lexicographicMode = False
    )

    total = 0
    sum = 0

    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                total += 1
                sum += varBind[1]

    res = sum / total
    return int(res)

def decode_snmp_date(octetstr: bytes) -> datetime.datetime:
    size = len(octetstr)
    if size == 8:
        (year, month, day, hour, minutes, 
         seconds, deci_seconds,
        ) = struct.unpack('>HBBBBBB', octetstr)
        return datetime.datetime(
            year, month, day, hour, minutes, seconds, 
            deci_seconds * 100_000, tzinfo = pytz.utc)
    elif size == 11:
        (year, month, day, hour, minutes, 
         seconds, deci_seconds, direction, 
         hours_from_utc, minutes_from_utc,
        ) = struct.unpack('>HBBBBBBcBB', octetstr)
        offset = datetime.timedelta(
            hours = hours_from_utc, minutes = minutes_from_utc)
        if direction == b'-':
            offset = -offset 
        return datetime.datetime(
            year, month, day, hour, minutes, seconds, 
            deci_seconds * 100_000, tzinfo = pytz.utc) + offset
    raise ValueError('The provided OCTETSTR is not a valid SNMP date')