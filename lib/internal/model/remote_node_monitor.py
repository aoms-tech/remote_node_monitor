from lib.external.pythontools.dict_adaptable import DictAdaptable

from lib.external.mCommon3.model.serialcomm import SerialConfig


class BEBoardConfig(DictAdaptable):
    LogFilePath: str


class GoogleDriveConfig(DictAdaptable):
    SyncFrequency: int
    LocalLogPath: str
    RemoteLogPath: str


class RemoteNodeMonitorConfig(DictAdaptable):
    Nucleo: SerialConfig
    GoogleDrive: GoogleDriveConfig
    Skyla1: BEBoardConfig
    Creed1: BEBoardConfig
    Skyla2: BEBoardConfig
    Creed2: BEBoardConfig
