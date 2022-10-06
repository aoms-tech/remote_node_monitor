import logging
from logging.handlers import TimedRotatingFileHandler
import serial
import time

from lib.internal.model.remote_node_monitor import RemoteNodeMonitorConfig

from lib.external.mCommon3.service.avrdude_service import program_board


def setup_logger(name, log_file, level=logging.INFO, rotating=1):
    formatter = logging.Formatter('%(asctime)s %(message)s')
    if rotating:
        handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1)
        handler.suffix = "%Y%m%d"
        handler.setFormatter(formatter)
    else:
        handler = logging.FileHandler(filename=log_file)
        handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(stream_handler)

    return logger


def run_monitor_application(config: RemoteNodeMonitorConfig):
    config.Nucleo.Serial = serial.Serial(config.Nucleo.Port, config.Nucleo.Baud)
    config.Nucleo.Serial.close()
    config.Nucleo.Serial.open()

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
    from pyrclone import Rclone
    from pyrclone import RcloneError

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
    import piplates.RELAYplate as RelayHat

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


def run_controller_application(config: RemoteNodeMonitorConfig):
    import piplates.RELAYplate as RelayHat
    from serial.tools import list_ports

    # Set off state for relays
    RelayHat.relayOFF(0, 1)     # Skyla1 UPDI
    RelayHat.relayOFF(0, 2)     # Creed1 UPDI
    RelayHat.relayOFF(0, 3)     # Skyla2 UPDI
    RelayHat.relayOFF(0, 4)     # Creed2 UPDI
    RelayHat.relayOFF(0, 5)     # Skyla1 and Skyla2 pwr_en
    RelayHat.relayOFF(0, 6)     # Radio Module 1
    RelayHat.relayOFF(0, 7)     # Radio Module 2

    print("Waiting 10 seconds before starting up skyla ...")
    for i in range(1, 11):
        print(f"Progress: {i}/10 seconds", end='\r')
        time.sleep(1)

    # Blues logger setup
    blues1_logger = setup_logger('blues_logger1', config.GoogleDrive.LocalLogPath + '/blues1.log')
    blues2_logger = setup_logger('blues_logger2', config.GoogleDrive.LocalLogPath + '/blues2.log')
    blues1_logger.info("Starting blues notecard 1 logging script ...")
    blues2_logger.info("Starting blues notecard 2 logging script ...")

    # Find blues module serial ports
    ports_before_list = list_ports.comports()
    RelayHat.relayON(0, 5)      # Skyla1 and Skyla2 pwr_en
    RelayHat.relayON(0, 6)      # Radio Module 1
    time.sleep(2)
    ports_middle_list = list_ports.comports()
    for port in ports_middle_list:
        if port not in ports_before_list:
            config.Creed1.Blues.Serial.Port = port.device

    RelayHat.relayON(0, 7)      # Radio Module 2
    time.sleep(2)
    ports_end_list = list_ports.comports()
    for port in ports_end_list:
        if port not in ports_middle_list:
            config.Creed2.Blues.Serial.Port = port.device

    config.Creed1.Blues.Serial.Serial = serial.Serial(config.Creed1.Blues.Serial.Port, config.Creed1.Blues.Serial.Baud)
    config.Creed2.Blues.Serial.Serial = serial.Serial(config.Creed2.Blues.Serial.Port, config.Creed2.Blues.Serial.Baud)
    config.Creed1.Blues.Serial.Serial.write(b'{"req":"card.trace","trace":"+mdmmax", "mode":"on"}\r\n')
    config.Creed2.Blues.Serial.Serial.write(b'{"req":"card.trace","trace":"+mdmmax", "mode":"on"}\r\n')

    while 1:
        blues1_line = config.Creed1.Blues.Serial.Serial.readline()
        blues2_line = config.Creed2.Blues.Serial.Serial.readline()

        if blues1_line:
            blues1_logger.info(blues1_line)
            # print(blues1_line)
        if blues2_line:
            blues2_logger.info(blues2_line)
            # print(blues2_line)


def run_reset_application():
    import piplates.RELAYplate as RelayHat

    print("Turning off relay to remove ground from Skyla's pwr_en ...")
    RelayHat.relayOFF(0, 5)
    RelayHat.relayOFF(0, 6)
    RelayHat.relayOFF(0, 7)
    # print("Waiting 10 seconds ...")
    for i in range(1, 11):
        print(f"Progress: {i}/10 seconds", end='\r')
        time.sleep(1)
    print()
    print("Turning relay back on to connect Skyla's pwr_en to ground ...")
    RelayHat.relayON(0, 5)
    print("Complete. Exiting reset application.")


def run_init_relays():
    import piplates.RELAYplate as RelayHat

    RelayHat.relayOFF(0, 1)     # Skyla1 UPDI
    RelayHat.relayOFF(0, 2)     # Creed1 UPDI
    RelayHat.relayOFF(0, 3)     # Skyla2 UPDI
    RelayHat.relayOFF(0, 4)     # Creed2 UPDI
    RelayHat.relayON(0, 5)      # Skyla1 and Skyla2 pwr_en
    RelayHat.relayOFF(0, 6)     # Radio Module 1
    RelayHat.relayOFF(0, 7)     # Radio Module 2


def get_info_table(b, a):
    spacer_amount = 45

    headings = ['INFORMATION', 'BEFORE', 'AFTER']
    string = (headings[0] + (" " * (spacer_amount - len(headings[0]))) + headings[1] + (
                " " * (spacer_amount - len(headings[1]))) + headings[2] + '\n')
    for key in b:
        if type(b[key]) == dict:
            for nested_key in b[key]:
                intro = key + '/' + nested_key + ":"
                string += intro + (" " * (spacer_amount - len(intro))) + str(b[key][nested_key]) + (
                            " " * (spacer_amount - len(str(b[key][nested_key])))) + "%s\n" % a[key][nested_key]
        else:
            intro = key + ":"
            string += intro + (" " * (spacer_amount - len(intro))) + str(b[key]) + (
                        " " * (spacer_amount - len(str(b[key])))) + "%s\n" % a[key]

    return string


def run_molly(config: RemoteNodeMonitorConfig):
    from lib.external.mCommon3.service.skyla_service import update_app_key, update_net_key, update_creed_settings
    from lib.external.mCommon3.service.skyla_service import update_keys_dataframe_from_vault, generate_skyla_payload
    import subprocess
    import datetime

    monitor_stop_command = f'sudo systemctl stop remoteNodeMonitor.service'
    subprocess.run(monitor_stop_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)

    reset_command = f'sudo st-flash reset'
    subprocess.run(reset_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)

    config.Nucleo.Serial = serial.Serial(port=config.Nucleo.Port, baudrate=config.Nucleo.Baud)

    config.Nucleo.Serial.close()
    config.Nucleo.Serial.open()

    molly_logger_file_name = config.GoogleDrive.LocalLogPath + datetime.datetime.now().strftime(
        "/%Y%m%d_%H%M%S_molly.log")
    molly_logger = setup_logger("molly_logger", molly_logger_file_name, rotating=1)

    if not config.Skyla1.Molly and not config.Skyla2.Molly:
        molly_logger.info(
            "Both Skyla1 and Skyla2 have 'Molly' set to false in settings_molly file. Update and try again.")
        molly_logger.info("Exiting.")
        exit(0)

    if config.Skyla1.Molly:
        update_keys_dataframe_from_vault(config.Skyla1.Settings)
        update_app_key(config.Skyla1.Settings)
        update_net_key(config.Skyla1.Settings)
        update_creed_settings(config.Skyla1.Settings)
        skyla1_payload = generate_skyla_payload(config.Skyla1.Settings)
        molly_logger.info(f"Skyla1 payload: {skyla1_payload}")
        run_reset_application()
        molly_logger.info("Running Molly application on Skyla1 ...")
        config.Nucleo.Serial.write(b'p')

        skyla1_dict = {
            "B": {},
            "A": {}
        }

        while 1:
            line = config.Nucleo.Serial.readline()
            if line:
                try:
                    line = line.decode('utf-8').strip()
                except:
                    continue
                else:
                    if "S1|" in line:
                        try:
                            contents = line.split("|")
                            skyla1_dict[contents[1]][contents[2]] = contents[3]
                        except:
                            # print(line)
                            continue

                    if "send payload" in line:
                        config.Nucleo.Serial.write(skyla1_payload)

                    if "molly complete" in line:
                        break

        molly_logger.info(
            "=== SKYLA1 MOLLY OUTPUT ============================================================================"
            "================================================")
        molly_logger.info(get_info_table(skyla1_dict["B"], skyla1_dict["A"]))
        molly_logger.info("Done Mollying Skyla1.")

    if config.Skyla2.Molly:
        update_keys_dataframe_from_vault(config.Skyla2.Settings)
        update_app_key(config.Skyla2.Settings)
        update_net_key(config.Skyla2.Settings)
        update_creed_settings(config.Skyla2.Settings)
        skyla2_payload = generate_skyla_payload(config.Skyla2.Settings)
        molly_logger.info(f"Skyla2 payload: {skyla2_payload}")
        run_reset_application()
        molly_logger.info("Running Molly application on Skyla2 ...")
        config.Nucleo.Serial.write(b'q')

        skyla2_dict = {
            "B": {},
            "A": {}
        }

        while 1:
            line = config.Nucleo.Serial.readline()
            if line:
                try:
                    line = line.decode('utf-8').strip()
                except:
                    continue
                else:
                    if "S2|" in line:
                        try:
                            contents = line.split("|")
                            skyla2_dict[contents[1]][contents[2]] = contents[3]
                        except:
                            continue

                    if "send payload" in line:
                        config.Nucleo.Serial.write(skyla2_payload)

                    if "molly complete" in line:
                        break

        molly_logger.info(
            "=== SKYLA2 MOLLY OUTPUT ============================================================================"
            "================================================")
        molly_logger.info(get_info_table(skyla2_dict["B"], skyla2_dict["A"]))
        molly_logger.info("Done Mollying Skyla2.")

    molly_logger.info("Exiting. Please reset Pi now.")


# todo: have molly messages save to log file
# todo: fix the logging repo and put into our file structures
