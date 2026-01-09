# RFID–NFC Card Reader & Desktop Management System  
**Library Automation Project (Summer Internship)**

This project was developed during my **4th Semester Summer Internship** under **Manipur Technical University, Manipur**.  
The goal of this work was to **upgrade a traditional barcode-based library system to an RFID-based system**, enabling faster, contactless, and more reliable student identification and book circulation using **RFID/NFC cards**.

The system integrates with **Koha Library Management System** workflows and also provides a **desktop application** for issuing, reading, and managing RFID cards.

## Internship Details

- **Internship Type:** Summer Internship
- **Institution:** Manipur Technical University, Manipur  
- **Project Domain:** Library Automation / RFID Systems  
- **Focus Area:** Replacing barcode scanning with RFID/NFC technology  

## Project Overview

The project consists of two main parts:

### 1 RFID / NFC Card Reader (Python)
A Python-based RFID card reader inspired by `pcsc_scan`, capable of:
- Detecting card insertion and removal
- Reading the card **UID (Unique Identifier)**
- Writing basic user information to RFID cards
- Storing card data locally for management and tracking

### 2 RFID Manager Desktop Application
A lightweight **desktop application** for library administrators to:
- Register new RFID cards
- Manage student and faculty records
- Read and write RFID cards
- Support Koha-friendly workflows for borrowing and returning books

## Key Features

### RFID / NFC Card Reader
- Detects card insertion and removal events
- Reads card UID
- Reads optional data from **MIFARE Classic block 4**
- Writes user name to RFID card (up to 16 ASCII characters)
- Stores card data in a local JSON database

### RFID Manager Desktop App
- GUI-based desktop application (Tkinter)
- CLI fallback for systems without GUI
- CRUD operations for students and faculty
- Automatic UID capture from scanned cards
- Local SQLite database for record storage
- Koha-compatible workflows

## Technology Stack

| Layer                |        Technology |
|----------------------|-------------------|
| Programming Language |       Python 3.8+ |
| RFID Library         |           pyscard |
| GUI                  |           Tkinter |
| Database             |            SQLite |
| RFID Reader          |  PC/SC-compatible |

## Project Structure
├── app_cli.py
├── app.py
├── card_db.json
├── cards.db
├── db.py
├── __pycache__
│   ├── app_cli.cpython-310.pyc
│   ├── app.cpython-310.pyc
│   ├── db.cpython-310.pyc
│   └── rfid.cpython-310.pyc
├── README.md
└── rfid.py

## Requirements
- Python 3.8 or higher
- `pyscard` library
- PC/SC-compatible RFID/NFC reader (e.g. ACR122U)
- On Linux:
  - `pcscd` (PC/SC daemon)
  - `libccid`
  - `python3-tk` (for GUI)

## Installation

## Install Python dependency
```bash
python3 -m pip install --user pyscard

## Install Tkinter
- sudo apt update
- sudo add-apt-repository universe
- sudo apt update
- sudo apt install -y python3-tk

## Start PC/SC service
- sudo systemctl start pcscd
- sudo systemctl enable pcscd

## Running the Project
- Run the GUI application
- python3 app.py

## Run the CLI fallback
- python3 app_cli.py


## Koha Integration Notes
- Recommended: Use a keyboard-wedge (HID) RFID reader.
- The card UID will automatically appear in Koha’s search bar.
- If the reader is not HID:
- Use this app to scan and copy the UID into Koha, or
- Extend the app with a small local API for automatic UID forwarding.

## Troubleshooting
- Tkinter not found
- ModuleNotFoundError: No module named 'tkinter'
- Install python3-tk

## Reader not detected
- pcsc_scan
or
- python3 - <<'PY'
from smartcard.System import readers
- print(readers())
- PY

## USB permission issues

- Create a udev rule:
SUBSYSTEM=="usb", ATTR{idVendor}=="072f", ATTR{idProduct}=="2200", MODE="0664", GROUP="plugdev"
- Reload udev:
sudo udevadm control --reload-rules && sudo udevadm trigger

## Security Notes
- Data written to RFID cards is not secure authentication data
- Intended only for human-readable identification
- Regularly back up cards.db
- For production:
- Use server-side DB
- Secure API
- Authentication and authorization

## Future Enhancements
- CSV import/export for bulk enrollment
- Faculty authentication system
- HTTP API for Koha integration
- Improved GUI using PyQt / PySide
- Role-based access control

## Author
Bornison Okram
Computer Science Student 

This project was developed as part of an academic internship and is intended for educational and research purposes.

