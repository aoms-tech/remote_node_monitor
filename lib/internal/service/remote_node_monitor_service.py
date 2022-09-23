import logging
from logging.handlers import TimedRotatingFileHandler
import serial
import time
from pyrclone import Rclone
from pyrclone import RcloneError
import piplates.RELAYplate as RelayHat

from lib.internal.model.remote_node_monitor import RemoteNodeMonitorConfig

from lib.external.mCommon3.service.avrdude_service import program_board


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


def run_programming_sequence(config: RemoteNodeMonitorConfig, brd_name):
    programming_attempts = 2
    print(f"Programming {brd_name}")
    for p in range(0, programming_attempts):
        try:
            programming_output = program_board(config.Programmer)
        except:
            print("Programming timed out.")
            if p == programming_attempts - 1:
                print(f"Failed programming {brd_name}.")
            else:
                print(f"Attempting program again ... {p + 1}/{programming_attempts}")
        else:
            if b'verified' in programming_output.stdout:
                print(f"Programming {brd_name} Successful!!!!!")
                break
            else:
                print("Board programming not verified.")
                if p == programming_attempts - 1:
                    print(f"Failed programming {brd_name}.")
                else:
                    print(f"Attempting program again ... {p + 1}/{programming_attempts}")


def run_programming_application(config: RemoteNodeMonitorConfig):
    RelayHat.relayOFF(0, 1)  # Skyla1 UPDI
    RelayHat.relayOFF(0, 2)  # Creed1 UPDI
    RelayHat.relayOFF(0, 3)  # Skyla2 UPDI
    RelayHat.relayOFF(0, 4)  # Creed2 UPDI

    if config.Skyla1.Program:
        RelayHat.relayON(0, 1)
        config.Programmer.HexPath = config.Skyla1.ProgrammingHexPath
        run_programming_sequence(config, 'Skyla1')
        RelayHat.relayOFF(0, 1)

    if config.Creed1.Program:
        RelayHat.relayON(0, 2)
        config.Programmer.HexPath = config.Creed1.ProgrammingHexPath
        run_programming_sequence(config, 'Creed1')
        RelayHat.relayOFF(0, 2)

    if config.Skyla2.Program:
        RelayHat.relayON(0, 3)
        config.Programmer.HexPath = config.Skyla2.ProgrammingHexPath
        run_programming_sequence(config, 'Skyla2')
        RelayHat.relayOFF(0, 3)

    if config.Creed2.Program:
        RelayHat.relayON(0, 4)
        config.Programmer.HexPath = config.Creed2.ProgrammingHexPath
        run_programming_sequence(config, 'Creed2')
        RelayHat.relayOFF(0, 4)


def run_reset_application():
    print("Turning off relay to remove ground from Skyla's pwr_en ...")
    RelayHat.relayOFF(0, 5)
    print("Waiting 10 seconds ...")
    for i in range(1, 11):
        print(f"Progress: {i}/10")
        time.sleep(1)
    print("Turning relay back on to connect Skyla's pwr_en to ground ...")
    RelayHat.relayON(0, 5)
    print("Complete. Exiting.")


def run_init_relays():
    RelayHat.relayOFF(0, 1)     # Skyla1 UPDI
    RelayHat.relayOFF(0, 2)     # Creed1 UPDI
    RelayHat.relayOFF(0, 3)     # Skyla2 UPDI
    RelayHat.relayOFF(0, 4)     # Creed2 UPDI
    RelayHat.relayON(0, 5)      # Skyla1 and Skyla2 pwr_en
    RelayHat.relayOFF(0, 6)     # Radio Module 1
    RelayHat.relayOFF(0, 7)     # Radio Module 2
