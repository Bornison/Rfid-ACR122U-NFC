"""Command-line fallback for RFID manager.

Use this when tkinter is not available. Provides basic CRUD and card scan/write.
"""
import sys
from typing import Optional

import db
import rfid


DB_PATH = "cards.db"


def prompt(prompt_text: str, default: Optional[str] = None) -> str:
    if default:
        return input(f"{prompt_text} [{default}]: ") or default
    return input(f"{prompt_text}: ")


def show_menu():
    print("\nRFID CLI Manager")
    print("1) List records")
    print("2) Add record")
    print("3) Update record")
    print("4) Delete record")
    print("5) Scan card")
    print("6) Write name to card")
    print("0) Exit")


def list_records():
    rows = db.list_persons(DB_PATH)
    if not rows:
        print("(no records)")
        return
    for r in rows:
        print(f"{r['id']:4} | {r.get('rfid_uid') or '':23} | {r['role']:7} | {r['name']}")


def add_record():
    data = {}
    data["rfid_uid"] = prompt("RFID UID (leave blank to scan)") or None
    data["role"] = prompt("Role (student/faculty)", "student")
    data["name"] = prompt("Name")
    data["department"] = prompt("Department")
    data["category"] = prompt("Category (for students)")
    data["program"] = prompt("Program")
    data["year"] = prompt("Year")
    db.add_person(data, DB_PATH)
    print("Added.")


def update_record():
    pid = int(prompt("Record ID to update"))
    person = db.get_person(pid, DB_PATH)
    if not person:
        print("Not found")
        return
    data = {}
    for key in ("rfid_uid", "role", "name", "department", "category", "program", "year"):
        data[key] = prompt(key, person.get(key) or "")
    db.update_person(pid, data, DB_PATH)
    print("Updated.")


def delete_record():
    pid = int(prompt("Record ID to delete"))
    confirm = prompt(f"Type YES to confirm deletion of {pid}")
    if confirm == "YES":
        db.delete_person(pid, DB_PATH)
        print("Deleted.")
    else:
        print("Aborted.")


def scan_card_action():
    print("Waiting for card (8s)...")
    conn = rfid.wait_for_card(timeout=8)
    if not conn:
        print("No card detected.")
        return
    uid, text = rfid.scan_card(conn)
    print("UID:", uid)
    print("Text:", text)
    if uid:
        existing = db.get_person_by_uid(uid, DB_PATH)
        if existing:
            print("Existing record:", existing.get("name"))
        else:
            if prompt("Register this UID? (y/N)", "N").lower() == "y":
                data = {
                    "rfid_uid": uid,
                    "role": prompt("Role (student/faculty)", "student"),
                    "name": prompt("Name"),
                    "department": prompt("Department"),
                    "category": prompt("Category"),
                    "program": prompt("Program"),
                    "year": prompt("Year"),
                }
                db.add_person(data, DB_PATH)
                print("Registered.")


def write_name_action():
    uid = prompt("RFID UID to target (leave blank to scan)")
    if not uid:
        print("Tap the card to write to it")
        conn = rfid.wait_for_card(timeout=8)
        if not conn:
            print("No card detected.")
            return
    else:
        try:
            conn = rfid.get_reader_connection()
            conn.connect()
        except Exception as e:
            print("Reader error:", e)
            return
    name = prompt("Name to write (max 16 chars)")[:16]
    ok = rfid.write_to_card_block(conn, name)
    print("Write OK" if ok else "Write failed")


def main():
    db.init_db(DB_PATH)
    while True:
        show_menu()
        choice = prompt("Choice")
        if choice == "1":
            list_records()
        elif choice == "2":
            add_record()
        elif choice == "3":
            update_record()
        elif choice == "4":
            delete_record()
        elif choice == "5":
            scan_card_action()
        elif choice == "6":
            write_name_action()
        elif choice == "0":
            print("Bye")
            sys.exit(0)
        else:
            print("Unknown choice")


if __name__ == "__main__":
    main()
