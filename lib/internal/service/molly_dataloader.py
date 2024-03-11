from lib.external.pythontools import crc8dallas


def concat_crc(payload: bytes):
    hsh = crc8dallas.calc(payload)
    crc = str(hsh)[2:]
    if len(crc) == 1:
        crc = '0' + crc

    message = payload + bytes.fromhex(crc)

    return message


def generate_skyla_payload_batched(generated_str: bytes):
    split_char = b'|'
    fill_char = b'0'
    batch_payload = {"id_and_keys": "", "settings": ""}
    item_splited = generated_str.split(split_char)
    option = item_splited.pop(0)
    item_splited.pop()

    batch_0_option = option[:4].ljust(13, fill_char)
    batch_0_values = item_splited[:4]
    batch_0_values = batch_0_values + [b'']*9
    batch_payload["id_and_keys"] = concat_crc(
        split_char.join([batch_0_option] + batch_0_values) + split_char)

    batch_1_option = option[4:]
    batch_1_option = b'1000' + batch_1_option
    batch_1_values = [item_splited[0]] + [b'']*3 + item_splited[4:]
    batch_payload["settings"] = concat_crc(split_char.join(
        [batch_1_option] + batch_1_values) + split_char)
    
    return batch_payload


def generate_skyla_payload_batched_concated(batch_payload: dict = None):
    id_and_keys_len = len(batch_payload["id_and_keys"]).to_bytes(1, "big")
    print(id_and_keys_len)
    setting_len = len(batch_payload["settings"]).to_bytes(1, "big")
    print(setting_len)
    
    return id_and_keys_len + setting_len + batch_payload["id_and_keys"] + batch_payload["settings"]
