import time
from smartcard.System import readers
from smartcard.Exceptions import NoCardException

# === CONFIG ===
GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
READ_BLOCK = [0xFF, 0xB0, 0x00, 0x04, 0x10]
AUTH_BLOCK = [0xFF, 0x86, 0x00, 0x00, 0x05,
              0x01, 0x00, 0x04, 0x60, 0x00]


def list_readers():
    """Return list of connected smartcard readers."""
    return readers()


def get_reader_connection(index=0):
    """Create and return a connection to the selected reader.

    Raises IndexError if no reader present.
    """
    r = list_readers()
    if not r:
        raise IndexError("No smartcard reader found")
    conn = r[index].createConnection()
    return conn


def write_to_card_block(conn, text, block=4):
    """Write up to 16 ASCII characters to the given block (MIFARE Classic).

    Returns True on success.
    """
    data = [ord(c) for c in text[:16].ljust(16)]
    cmd = [0xFF, 0xD6, 0x00, block, 0x10] + data
    response, sw1, sw2 = conn.transmit(cmd)
    return sw1 == 0x90


def scan_card(conn):
    """Read UID and (optionally) block-4 text from a tapped card.

    Returns (uid_hex, card_text) or (None, None) on failure.
    """
    try:
        uid, sw1, sw2 = conn.transmit(GET_UID)
        if sw1 != 0x90:
            return None, None
        uid_hex = ":".join([hex(x)[2:].zfill(2).upper() for x in uid])

        # Authenticate + read block 4
        _, sw1, sw2 = conn.transmit(AUTH_BLOCK)
        card_text = None
        if sw1 == 0x90:
            data, sw1, sw2 = conn.transmit(READ_BLOCK)
            if sw1 == 0x90:
                card_text = "".join([chr(x) for x in data if 31 < x < 127]).strip()
        return uid_hex, card_text
    except Exception:
        return None, None


def wait_for_card(timeout=None, reader_index=0, poll_interval=0.2):
    """Block until a card is present in the reader and return a connected connection.

    If timeout (seconds) provided, returns None on timeout.
    """
    start = time.time()
    while True:
        try:
            conn = get_reader_connection(reader_index)
            conn.connect()
            return conn
        except IndexError:
            # no reader
            time.sleep(poll_interval)
        except NoCardException:
            # reader present but no card
            if timeout and (time.time() - start) > timeout:
                return None
            time.sleep(poll_interval)


if __name__ == "__main__":
    # scanner loop for debugging
    print("RFID low-level test. Tap cards (Ctrl-C to quit)")
    try:
        while True:
            try:
                conn = get_reader_connection()
                conn.connect()
                uid, text = scan_card(conn)
                if uid:
                    print("UID:", uid, "Text:", text)
                time.sleep(0.5)
            except IndexError:
                print("No reader found. Waiting...")
                time.sleep(1)
            except NoCardException:
                time.sleep(0.2)
    except KeyboardInterrupt:
        print("Stopped")