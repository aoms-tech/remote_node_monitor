from lib.external.pythontools.dict_adaptable import DictAdaptable

from lib.external.mCommon3.model.serialcomm import SerialConfig
from lib.external.mCommon3.model.avrdude import AVRDudeConfig
from lib.external.mCommon3.model.skyla import SkylaConfig


class BluesConfig(DictAdaptable):
    Serial: SerialConfig


class BEBoardConfig(DictAdaptable):
    Molly: bool
    Program: bool
    LogFilePath: str
    ProgrammingHexPath: str
    Settings: SkylaConfig
    Blues: BluesConfig


class DigitalOceanConfig(DictAdaptable):
    Mode: int           # 1 = frequency, 2 = daily at X hour
    SyncFrequency: int
    ResetDailyTime: int
    LocalLogPath: str
    RemoteObserverLogPath: str
    AccessKey: str
    SecretAccessKey: str
    BucketName: str
    Endpoint: str
    Region: str

class NodeSettings(DictAdaptable):
    ChargerEnable: bool
    SelectSens: dict
    NodeEnabled: bool

class RemoteNodeMonitorConfig(DictAdaptable):
    BluesTraceFrequencyMinutes: int
    Nucleo: SerialConfig
    DigitalOcean: DigitalOceanConfig
    Programmer: AVRDudeConfig
    Skyla1: BEBoardConfig
    Creed1: BEBoardConfig
    Skyla2: BEBoardConfig
    Creed2: BEBoardConfig
    Node1: NodeSettings
    Node2: NodeSettings