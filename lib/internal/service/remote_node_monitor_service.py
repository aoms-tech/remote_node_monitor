import logging
from logging.handlers import TimedRotatingFileHandler
import serial
import time
from pyrclone import Rclone
from pyrclone import RcloneError

from lib.internal.model.remote_node_monitor import RemoteNodeMonitorConfig


def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1)
    handler.suffix = "%Y%m%d"
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def run_monitor_application(config: RemoteNodeMonitorConfig):
    config.Nucleo.Serial = serial.Serial(config.Nucleo.Port, config.Nucleo.Baud)

    skyla1_logger = setup_logger('skyla1', config.Skyla1.LogFilePath)
    creed1_logger = setup_logger('creed1', config.Creed1.LogFilePath)
    skyla2_logger = setup_logger('skyla2', config.Skyla2.LogFilePath)
    creed2_logger = setup_logger('creed2', config.Creed2.LogFilePath)

    skyla1_logger.info("Script startup.")
    creed1_logger.info("Script startup.")
    skyla2_logger.info("Script startup.")
    creed2_logger.info("Script startup.")

    while 1:
        line = config.Nucleo.Serial.readline()
        if line:
            try:
                line = line.decode('utf-8').strip()
            except:
                pass
            prefix = line[:3]
            print(line)
            if prefix == "S1|":
                skyla1_logger.info(line[3:])
            elif prefix == "C1|":
                creed1_logger.info(line[3:])
            elif prefix == "S2|":
                skyla2_logger.info(line[3:])
            elif prefix == "C2|":
                creed2_logger.info(line[3:])


def run_drive_sync_application(config: RemoteNodeMonitorConfig):
    logger = setup_logger('rclone_logger', config.GoogleDrive.LocalLogPath+'/ggl_dr_sync.log')
    logger.info("Starting google drive sync script ...")
    timer_start = time.time()
    while 1:
        if time.time() - timer_start > config.GoogleDrive.SyncFrequency:
            output = Rclone().copy(config.GoogleDrive.LocalLogPath, config.GoogleDrive.RemoteLogPath)

            if output.return_code is not RcloneError.SUCCESS:
                logger.info(output.error)
            else:
                logger.info("Google drive updated.")
            timer_start = time.time()
