from lib.external.pythontools.dict_adaptable import DictAdaptable

from lib.external.mCommon3.model.serialcomm import SerialConfig
from lib.external.mCommon3.model.avrdude import AVRDudeConfig


class BEBoardConfig(DictAdaptable):
    Program: bool
    LogFilePath: str
    ProgrammingHexPath: str


class GoogleDriveConfig(DictAdaptable):
    SyncFrequency: int
    LocalLogPath: str
    RemoteLogPath: str


class RemoteNodeMonitorConfig(DictAdaptable):
    Nucleo: SerialConfig
    GoogleDrive: GoogleDriveConfig
    Programmer: AVRDudeConfig
    Skyla1: BEBoardConfig
    Creed1: BEBoardConfig
    Skyla2: BEBoardConfig
    Creed2: BEBoardConfig