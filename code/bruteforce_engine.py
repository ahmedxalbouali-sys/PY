"""
bruteforce_engine.py
====================

Core brute-force engine.

Features:
- ZIP / 7Z / PDF support
- Correct positional mask handling
- Accurate total combination calculation
- Multithreaded password testing
- Safe cancellation
- Clean producer-consumer architecture

Author: Ahmed Bouali
Date: 2025-12-22
"""

import itertools
import threading
from queue import Queue, Empty

from testpass import (
    test_zip,
    test_7z,
    test_pdf,
    is_zip_protected,
    is_7z_protected,
    is_pdf_protected
)

# ==========================================================
# DEFAULT CONFIGURATION
# ==========================================================
DEFAULT_CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"
DEFAULT_MIN_LEN = 4
DEFAULT_MAX_LEN = 8
DEFAULT_THREADS = 8
QUEUE_MAX_SIZE = 5000


# ==========================================================
# FILE TYPE DETECTION
# ==========================================================
def detect_file_type(path):
    """
    Detects the file type AND ensures it is password protected.
    """
    if path.endswith(".zip") and is_zip_protected(path):
        return "zip"
    if path.endswith(".7z") and is_7z_protected(path):
        return "7z"
    if path.endswith(".pdf") and is_pdf_protected(path):
        return "pdf"
    raise ValueError("Unsupported or unprotected file")


# ==========================================================
# MASK PARSER
# ==========================================================
def parse_table(table_string):
    """
    Converts a pipe-separated mask string into a positional table.

    Example:
    "a|bc||9"  →  [['a'], ['b','c'], None, None, ['9']]
    """
    if not table_string:
        return []

    table = []
    for part in table_string.split("|"):
        if part == "":
            table.append(None)      # Unknown position
        else:
            table.append(list(part))  # Allowed characters
    return table


# ==========================================================
# TOTAL COMBINATION CALCULATOR
# ==========================================================
def calculate_total_combinations(min_len, max_len, charset, table):
    """
    Calculates the exact number of password combinations.
    """
    total = 0
    charset_size = len(charset)

    for length in range(min_len, max_len + 1):
        count = 1
        for pos in range(length):
            if pos < len(table) and table[pos] is not None:
                count *= len(table[pos])
            else:
                count *= charset_size
        total += count

    return total


# ==========================================================
# PASSWORD GENERATOR (POSITIONAL – FIXED)
# ==========================================================
def password_generator(min_len, max_len, charset, table):
    """
    Generates passwords while respecting exact character positions.
    """
    for length in range(min_len, max_len + 1):

        # Build per-position character sets
        position_sets = []

        for pos in range(length):
            if pos < len(table) and table[pos] is not None:
                position_sets.append(table[pos])
            else:
                position_sets.append(charset)

        # Cartesian product over all positions
        for combo in itertools.product(*position_sets):
            yield "".join(combo)


# ==========================================================
# MAIN BRUTE-FORCE ENGINE
# ==========================================================
def brute_force_attack(
    file_path,
    min_len,
    max_len,
    charset,
    table_string,
    thread_count,
    progress_callback,
    stop_flag
):
    """
    Orchestrates the brute-force attack using multithreading.
    """

    file_type = detect_file_type(file_path)
    table = parse_table(table_string)

    total_combinations = calculate_total_combinations(
        min_len, max_len, charset, table
    )

    password_queue = Queue(maxsize=QUEUE_MAX_SIZE)
    producer_done = threading.Event()

    tested = 0
    tested_lock = threading.Lock()

    result = {"password": None}

    # ======================================================
    # WORKER THREAD
    # ======================================================
    def worker():
        nonlocal tested

        while not stop_flag.is_set():
            try:
                pwd = password_queue.get(timeout=0.3)
            except Empty:
                if producer_done.is_set():
                    return
                continue

            # Test password against correct file type
            if file_type == "zip":
                success = test_zip(file_path, pwd)
            elif file_type == "7z":
                success = test_7z(file_path, pwd)
            else:
                success = test_pdf(file_path, pwd)

            # Update progress safely
            with tested_lock:
                tested += 1
                progress_callback(tested, total_combinations)

            if success:
                result["password"] = pwd
                stop_flag.set()

            password_queue.task_done()

    # ======================================================
    # START WORKERS
    # ======================================================
    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    # ======================================================
    # PRODUCER
    # ======================================================
    for pwd in password_generator(min_len, max_len, charset, table):
        if stop_flag.is_set():
            break
        password_queue.put(pwd)

    producer_done.set()
    password_queue.join()

    return result["password"]
