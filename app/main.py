import subprocess
import logging
import sqlite3
from datetime import datetime, timedelta
import time
import os

# Set up logging
log_dir = "/var/log"
log_file_path = os.path.join(log_dir, "server_reboot.log")

# Check if the log file exists; if not, create it by logging an initial message
if not os.path.exists(log_file_path):
    logging.info(f"[+] !!! Log File SECTION !!! [+]")
    open(log_file_path, 'a').close()
    logging.info(f"[+] Log file created at {datetime.now()}")
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# Define the database directory and path
db_dir = "/etc"
db_path = os.path.join(db_dir, "reboot_schedule.db")

# Ensure the database directory exists
if not os.path.exists(db_dir):

    logging.info("[+] !!! WELCOME TO REBOOT MANAGER SCRIPT !!! [+]")

    print("[+] First run, creating database file...")
    os.makedirs(db_dir)

else:

    logging.info("[+] !!! REBOOT MANAGER SCRIPT RESUMED !!! [+]")

    print("[+] Welcome back: resuming application...!!!...")

# Define the reboot command
reboot_command = ["sudo", "reboot"]


def setup_database():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
         CREATE TABLE IF NOT EXISTS reboots (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             last_reboot TIMESTAMP,
             next_reboot TIMESTAMP,
             first_reboot TIMESTAMP,
             first_run_stat BOOLEAN,
             first_run_time TIMESTAMP,
             reboot_count INTEGER
         )
     ''')
    conn.commit()
    c.execute('SELECT COUNT(*) FROM reboots')
    if c.fetchone()[0] == 0:
        first_run_time = datetime.now()
        c.execute('''
            INSERT INTO reboots (first_reboot, first_run_stat, first_run_time, reboot_count)
            VALUES (?, ?, ?, ?)
        ''', (first_run_time + timedelta(hours=3), True, first_run_time, 0))
        conn.commit()
    conn.close()


def get_reboot_info():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        'SELECT last_reboot, next_reboot, first_reboot, first_run_stat, first_run_time, reboot_count FROM reboots ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    return row


def get_last_reboot_time():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        'SELECT last_reboot, next_reboot, first_reboot, first_run_stat, first_run_time, reboot_count FROM reboots ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    row = c.fetchone()
    conn.close()
    logging.info("[+] last rebooted time successfully fetched...")
    return row[0] if row else None


def update_last_reboot_time():
    logging.info("[+] Initiating updating last rebooted time...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO reboots (last_reboot) VALUES (?)', (datetime.now(),))
    conn.commit()
    logging.info("[+] last rebooted time successfully updated...")
    conn.close()


def update_reboot_info(last_reboot, next_reboot, first_reboot, first_run_stat, first_run_time, reboot_count):
    logging.info("[+] Initiating updating last rebooted time...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO reboots (last_reboot, next_reboot, first_reboot, first_run_stat, first_run_time, reboot_count)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (last_reboot, next_reboot, first_reboot, first_run_stat, first_run_time, reboot_count))
    conn.commit()
    conn.close()
    logging.info("[+] last rebooted time successfully updated...")


def reboot_server():
    try:
        logging.info("[+] Initiating server reboot...")

        # Get the current reboot information
        reboot_info = get_reboot_info()

        if reboot_info:
            last_reboot, next_reboot, first_reboot, first_run_stat, first_run_time, reboot_count = reboot_info
            reboot_count += 1
        else:
            first_reboot = datetime.now() + timedelta(hours=3)
            first_run_time = datetime.now()
            reboot_count = 1
            first_run_stat = True

        last_reboot = datetime.now()
        next_reboot = last_reboot + timedelta(hours=3)

        # Log the reboot time in the database
        logging.info(f"[+] Updating reboot time in the database.")
        update_reboot_info(last_reboot, next_reboot, first_reboot, first_run_stat, first_run_time, reboot_count)
        logging.info(f"[+] Reboot time in the database updated successfully.")

        # Execute the reboot command
        logging.info(f"[+] Starting server reboot now....")
        subprocess.run(reboot_command, check=True)

        logging.info(f"[+] Server reboot command executed successfully at {datetime.now()}.")

    except subprocess.CalledProcessError as e:
        logging.error(f"[-] An error occurred while initiating the reboot: {e}")


def schedule_next_reboot():
    logging.info(f"[+] Getting reboot info before scheduling.")
    reboot_info = get_reboot_info()

    if reboot_info:
        logging.info(f"[+] Reboot info successfully fetched from the DB.")
        last_reboot, next_reboot, first_reboot, first_run_stat, first_run_time, reboot_count = reboot_info
        next_reboot_time = datetime.strptime(next_reboot, '%Y-%m-%d %H:%M:%S.%f')
    else:
        logging.info(f"[+] No reboot info seen.\n\t[+] Scheduling....")
        next_reboot_time = datetime.now() + timedelta(hours=3)

    logging.info(f"[+] Scheduling next reboot at {next_reboot_time}")

    while datetime.now() < next_reboot_time:
        time.sleep(60)  # Check every minute

    reboot_server()


if __name__ == "__main__":
    if not os.path.exists(db_path):
        logging.info(f"[+] !!! DATABASE SECTION !!! [+]")
        logging.info(f"[+] Database tables and columns file created at {datetime.now()}")
        setup_database()

        # Log that the script has started
        logging.info("[+] !!! REBOOT MANAGER SCRIPT STARTED !!! [+]")

    schedule_next_reboot()
