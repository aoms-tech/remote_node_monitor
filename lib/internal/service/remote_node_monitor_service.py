#define Pi <--> Nucleo UART com consts
SKYLA1_PREFIX: str = "S1|"
SKYLA2_PREFIX: str = "S2|"
CREED1_PREFIX: str = "C1|"
CREED2_PREFIX: str = "C2|"

#DEV 1 => Skyla 1
#DEV 2 => Skyla 2
#DEV 3 => Creed 1
#DEV 4 => Creed 2
SETMODE_OBSERVE: bytes = b'a'
SETMODE_VALIDATE: bytes = b'b'
SETMODE_MOLLY_DEV1: bytes = b'c'
SETMODE_MOLLY_DEV2: bytes = b'd'
SETMODE_PROGRAM_DEV1: bytes = b'e'
SETMODE_PROGRAM_DEV2: bytes = b'f'
SETMODE_PROGRAM_DEV3: bytes = b'g'
SETMODE_PROGRAM_DEV4: bytes = b'h'
SETMODE_SENS_SELECT: bytes = b'i'
SETMODE_SET_CHG_STATE: bytes = b'j'
SETMODE_SET_DEV_PWR: bytes = b'k'

OFF: bytes = b'0'
ON: bytes = b'1'
CYCLE: bytes = b'2'

BOTH: bytes = b'0'
NODE1: bytes = b'1'
NODE2: bytes = b'2'

PI_PROCESS_FIN: bytes = b'`'

SERVICES = {
    'remoteNodeMonitor.service',
    'remoteNodeMonitorSync.service',
    'remoteNodeMonitorRelayInit.service'
}

import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import serial
import time
import yaml

from lib.internal.model.remote_node_monitor import RemoteNodeMonitorConfig

from lib.external.mCommon3.service.avrdude_service import program_board


# done :D
def run_init(config: RemoteNodeMonitorConfig):
    data = yaml.safe_load("settings_node.yaml")

    config.Nucleo.Serial = serial.Serial(config.Nucleo.Port, config.Nucleo.Baud)
    config.Nucleo.Serial.close()
    config.Nucleo.Serial.open()

    for node in [1, 2]:
        data = data[f"Node{node}"]

        run_charger_app(config, node, data)
        select_sensor(config, node, data)
        set_node_state(config, node, data)
        print(f"Node{node} initialization completed.")


# done :D
def set_node_state(config: RemoteNodeMonitorConfig, node: int, data: dict):
    if data["NodeEnabled"]:
        node_state = ON
        node_state_message = "ON"
    else:
        node_state = OFF
        node_state_message = "OFF"
    config.Nucleo.Serial.write(SETMODE_SET_CHG_STATE)
    config.Nucleo.Serial.write(bytes(node) + node_state)
    print(f"Settings state for Node{node} to {node_state_message}")


# done :D
def select_sensor(config: RemoteNodeMonitorConfig, node: int, data: dict):
    sensor_address = 0
    for sensor_is_selected in data["SelectSens"]:
        if sensor_is_selected:
            config.Nucleo.Serial.write(SETMODE_SENS_SELECT)
            config.Nucleo.Serial.write(bytes(node) + bytes(sensor_address))
            break
        sensor_address += 1
    print(f"Setting sensor for Node{node} to {data['SelectSens'][sensor_address]}")


# done :D
def run_charger_app(config: RemoteNodeMonitorConfig, node: int, data: dict):
    if data["ChargerEnable"]:
        charger_state = ON
        charger_state_message = "ON"
    else:
        charger_state = OFF
        charger_state_message = "OFF"
    config.Nucleo.Serial.write(SETMODE_SET_CHG_STATE)
    config.Nucleo.Serial.write(bytes(node) + charger_state)
    print(f"Settings charger for Node{node} to {charger_state_message}")


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
            print(line)
            try:
                line = line.decode('utf-8').strip()
            except:
                pass
            prefix = line[:3]
            if prefix == SKYLA1_PREFIX:
                skyla1_logger.info(line[3:])
            elif prefix == CREED1_PREFIX:
                creed1_logger.info(line[3:])
            elif prefix == SKYLA2_PREFIX:
                skyla2_logger.info(line[3:])
            elif prefix == CREED2_PREFIX:
                creed2_logger.info(line[3:])


#change to S3 bucket and change service scheduler to crontab
def run_drive_sync_application(config: RemoteNodeMonitorConfig):
    from pyrclone import Rclone
    from pyrclone import RcloneError
    import os

    logger = setup_logger('rclone_logger', config.GoogleDrive.LocalLogPath+'/ggl_dr_sync.log')
    logger.info("Starting google drive sync script ...")

    if config.GoogleDrive.Mode == 1:
        timer_start = time.time()
        while 1:
            if time.time() - timer_start > config.GoogleDrive.SyncFrequency:
                output = Rclone().copy(config.GoogleDrive.LocalLogPath, config.GoogleDrive.RemoteLogPath)

                if output.return_code is not RcloneError.SUCCESS:
                    logger.info(output.error)
                else:
                    for f in os.listdir(config.GoogleDrive.LocalLogPath):
                        if f[0].isnumeric():
                            os.remove(os.path.join(config.GoogleDrive.LocalLogPath, f))
                    logger.info("Google drive updated.")
                timer_start = time.time()

            file_list = os.listdir(config.GoogleDrive.LocalLogPath)
            filtered_file_list = [file for file in file_list if file[-1].isnumeric()]
            if filtered_file_list:
                for file in filtered_file_list:
                    new_filename = file[-8:] + "_" + file[:-9]
                    logger.info(f"Renaming {file} to {new_filename}")
                    os.rename(os.path.join(config.GoogleDrive.LocalLogPath, file),
                              os.path.join(config.GoogleDrive.LocalLogPath, new_filename))
    elif config.GoogleDrive.Mode == 2:
        last_date_synced = ""
        logger.info(datetime.datetime.now().hour)
        while 1:
            current_date = datetime.datetime.now()
            if current_date.day != last_date_synced:
                if current_date.hour == config.GoogleDrive.ResetDailyTime:
                    last_date_synced = current_date.day
                    output = Rclone().copy(config.GoogleDrive.LocalLogPath, config.GoogleDrive.RemoteLogPath)

                    if output.return_code is not RcloneError.SUCCESS:
                        logger.info(output.error)
                    else:
                        for f in os.listdir(config.GoogleDrive.LocalLogPath):
                            if f[0].isnumeric():
                                os.remove(os.path.join(config.GoogleDrive.LocalLogPath, f))
                        logger.info("Google drive updated.")

            file_list = os.listdir(config.GoogleDrive.LocalLogPath)
            filtered_file_list = [file for file in file_list if file[-1].isnumeric()]
            if filtered_file_list:
                for file in filtered_file_list:
                    new_filename = file[-8:] + "_" + file[:-9]
                    logger.info(f"Renaming {file} to {new_filename}")
                    os.rename(os.path.join(config.GoogleDrive.LocalLogPath, file),
                              os.path.join(config.GoogleDrive.LocalLogPath, new_filename))


#done
def suspend_services():
    import subprocess

    reset_commands = []

    for service in SERVICES:
        reset_commands.append(f'sudo systemctl stop {service}')

    for cmd in reset_commands:
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)


#done
def resume_services():
    import subprocess

    resume_commands = []

    for service in SERVICES:
        resume_commands.append(f'sudo systemctl start {service}')

    for cmd in resume_commands:
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)


#done
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


#need to re-run init after programming or molly
def run_programming_application(config: RemoteNodeMonitorConfig):

    config.Nucleo.Serial = serial.Serial(port=config.Nucleo.Port, baudrate=config.Nucleo.Baud, timeout=30)
    config.Nucleo.Serial.close()
    config.Nucleo.Serial.open()

    suspend_services()

    if config.Skyla1.Program:
        config.Nucleo.Serial.write(SETMODE_PROGRAM_DEV1)
        line = config.Nucleo.Serial.readline(1)
        if line:
            print(line)
            line = line.decode('utf-8').strip()
            if line == "Ready to program Sklya1":
                config.Programmer.HexPath = config.Skyla1.ProgrammingHexPath
                run_programming_sequence(config, 'Skyla1')
                run_reset_application(config, NODE1)
        else:
            print("Read error")
        config.Nucleo.Serial.write(PI_PROCESS_FIN)

    if config.Creed1.Program:
        config.Nucleo.Serial.write(SETMODE_PROGRAM_DEV3)
        line = config.Nucleo.Serial.readline(1)
        if line:
            print(line)
            line = line.decode('utf-8').strip()
            if line == "Ready to program Sklya1":
                config.Programmer.HexPath = config.Creed1.ProgrammingHexPath
                run_programming_sequence(config, 'Creed1')
                run_reset_application(config, NODE1)
        else:
            print("Read error")
        config.Nucleo.Serial.write(PI_PROCESS_FIN)

    if config.Skyla2.Program:
        config.Nucleo.Serial.write(SETMODE_PROGRAM_DEV2)
        line = config.Nucleo.Serial.readline(1)
        if line:
            print(line)
            line = line.decode('utf-8').strip()
            if line == "Ready to program Sklya1":
                config.Programmer.HexPath = config.Skyla2.ProgrammingHexPath
                run_programming_sequence(config, 'Skyla2')
                run_reset_application(config, NODE2)
        else:
            print("Read error")
        config.Nucleo.Serial.write(PI_PROCESS_FIN)

    if config.Creed2.Program:
        config.Nucleo.Serial.write(SETMODE_PROGRAM_DEV4)
        line = config.Nucleo.Serial.readline(1)
        if line:
            print(line)
            line = line.decode('utf-8').strip()
            if line == "Ready to program Sklya1":
                config.Programmer.HexPath = config.Creed2.ProgrammingHexPath
                run_programming_sequence(config, 'Creed2')
                run_reset_application(config, NODE2)
        else:
            print("Read error")
        config.Nucleo.Serial.write(PI_PROCESS_FIN)

    resume_services()
    print("Application complete. Resuming normal operation.")

#schedule this job using cron
#remove relayhat
def run_controller_application(config: RemoteNodeMonitorConfig):
    import subprocess
    import piplates.RELAYplate as RelayHat
    from serial.tools import list_ports


    #is this necessary?
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

    if not config.Creed1.Blues.Serial.Port and not config.Creed2.Blues.Serial.Port:
        blues1_logger.info("No port found for both Blues cards. Exiting.")
        blues2_logger.info("No port found for both Blues cards. Exiting.")

    if not config.Creed1.Blues.Serial.Port:
        for port in ports_before_list:
            if "ACM" in port.device:
                config.Creed1.Blues.Serial.Port = port.device

    if not config.Creed2.Blues.Serial.Port:
        for port in ports_before_list:
            if "ACM" in port.device:
                config.Creed2.Blues.Serial.Port = port.device

    config.Creed1.Blues.Serial.Serial = serial.Serial(config.Creed1.Blues.Serial.Port, config.Creed1.Blues.Serial.Baud,
                                                      timeout=10)
    config.Creed2.Blues.Serial.Serial = serial.Serial(config.Creed2.Blues.Serial.Port, config.Creed2.Blues.Serial.Baud,
                                                      timeout=10)
    config.Creed1.Blues.Serial.Serial.close()
    config.Creed2.Blues.Serial.Serial.close()
    config.Creed1.Blues.Serial.Serial.open()
    config.Creed2.Blues.Serial.Serial.open()

    config.Creed1.Blues.Serial.Serial.write(b'{"req":"card.trace","trace":"+mdmmax", "mode":"on"}\r\n')
    config.Creed2.Blues.Serial.Serial.write(b'{"req":"card.trace","trace":"+mdmmax", "mode":"on"}\r\n')

    reset_command = f'sudo st-flash reset'
    subprocess.run(reset_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)

    start_time = time.time()
    while 1:
        if time.time() - start_time > (config.BluesTraceFrequencyMinutes*60):
            blues1_logger.info("Sending trace message again ----------------------------------------------------------")
            blues2_logger.info("Sending trace message again ----------------------------------------------------------")
            config.Creed1.Blues.Serial.Serial.write(b'{"req":"card.trace","trace":"+mdmmax", "mode":"on"}\r\n')
            config.Creed2.Blues.Serial.Serial.write(b'{"req":"card.trace","trace":"+mdmmax", "mode":"on"}\r\n')
            start_time = time.time()

        blues1_line = config.Creed1.Blues.Serial.Serial.readline()
        blues2_line = config.Creed2.Blues.Serial.Serial.readline()

        if blues1_line:
            blues1_logger.info(blues1_line)
        if blues2_line:
            blues2_logger.info(blues2_line)


#done
def run_reset_application(config: RemoteNodeMonitorConfig, node: bytes = BOTH):

    config.Nucleo.Serial = serial.Serial(port=config.Nucleo.Port, baudrate=config.Nucleo.Baud, timeout=10)
    config.Nucleo.Serial.close()
    config.Nucleo.Serial.open()

    config.Nucleo.Serial.write(SETMODE_SET_DEV_PWR)
    config.Nucleo.Serial.write(node + CYCLE)
    #waits for Node to be powered ON, Nucleo waits 30seconds before powering ON when power cycling
    for i in range(30):
        print(f"Progress: {i}/30 seconds", end='\r')
        time.sleep(1)

    if node != NODE1 or NODE2 or BOTH:
        print("Invalid Node selection")
    else:
        if node == NODE1 or BOTH:
            line_n1 = config.Nucleo.Serial.readline().decode('utf-8').strip()
            print("Device1 ON") if "Dev1 ON" in line_n1 else print("Device1 OFF")
        if node == NODE2 or BOTH:
            line_n2 = config.Nucleo.Serial.readline().decode('utf-8').strip()
            print("Device2 ON") if "Dev2 ON" in line_n2 else print("Device2 OFF")

    print("Power cycle complete.")


#not used
def run_init_relays():
    import piplates.RELAYplate as RelayHat

    RelayHat.relayOFF(0, 1)     # Skyla1 UPDI
    RelayHat.relayOFF(0, 2)     # Creed1 UPDI
    RelayHat.relayOFF(0, 3)     # Skyla2 UPDI
    RelayHat.relayOFF(0, 4)     # Creed2 UPDI
    RelayHat.relayON(0, 5)      # Skyla1 and Skyla2 pwr_en
    RelayHat.relayOFF(0, 6)     # Radio Module 1
    RelayHat.relayOFF(0, 7)     # Radio Module 2


#done
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


#done
def run_molly(config: RemoteNodeMonitorConfig):
    from lib.external.mCommon3.service.skyla_service import update_app_key, update_net_key, update_creed_settings
    from lib.external.mCommon3.service.skyla_service import update_keys_dataframe_from_vault, generate_skyla_payload
    import subprocess
    import datetime

    monitor_stop_command = f'sudo systemctl stop remoteNodeMonitor.service'
    subprocess.run(monitor_stop_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)

    reset_command = f'sudo st-flash reset'
    out = subprocess.run(reset_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
    print(out.stdout)

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
        run_reset_application(config, NODE1)
        molly_logger.info("Running Molly application on Skyla1 ...")
        config.Nucleo.Serial.write(SETMODE_MOLLY_DEV1)

        skyla1_dict = {
            "B": {},
            "A": {}
        }

        while 1:
            line = config.Nucleo.Serial.readline()
            if line:
                print(line)
                try:
                    line = line.decode('utf-8').strip()
                except:
                    continue
                else:
                    if SKYLA1_PREFIX in line:
                        try:
                            contents = line.split("|")
                            skyla1_dict[contents[1]][contents[2]] = contents[3]
                        except:
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

    reset_command = f'sudo st-flash reset'
    out = subprocess.run(reset_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
    print(out.stdout)

    if config.Skyla2.Molly:
        update_keys_dataframe_from_vault(config.Skyla2.Settings)
        update_app_key(config.Skyla2.Settings)
        update_net_key(config.Skyla2.Settings)
        update_creed_settings(config.Skyla2.Settings)
        skyla2_payload = generate_skyla_payload(config.Skyla2.Settings)
        molly_logger.info(f"Skyla2 payload: {skyla2_payload}")
        run_reset_application(config, NODE2)
        molly_logger.info("Running Molly application on Skyla2 ...")
        config.Nucleo.Serial.write(SETMODE_MOLLY_DEV2)

        skyla2_dict = {
            "B": {},
            "A": {}
        }

        while 1:
            line = config.Nucleo.Serial.readline()
            if line:
                print(line)
                try:
                    line = line.decode('utf-8').strip()
                except:
                    continue
                else:
                    if SKYLA2_PREFIX in line:
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
