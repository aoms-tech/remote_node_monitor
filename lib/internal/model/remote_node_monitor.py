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


class GoogleDriveConfig(DictAdaptable):
    Mode: int           # 1 = frequency, 2 = daily at X hour
    SyncFrequency: int
    ResetDailyTime: int
    LocalLogPath: str
    RemoteLogPath: str


class RemoteNodeMonitorConfig(DictAdaptable):
    BluesTraceFrequencyMinutes: int
    Nucleo: SerialConfig
    GoogleDrive: GoogleDriveConfig
    Programmer: AVRDudeConfig
    Skyla1: BEBoardConfig
    Creed1: BEBoardConfig
    Skyla2: BEBoardConfig
    Creed2: BEBoardConfig
