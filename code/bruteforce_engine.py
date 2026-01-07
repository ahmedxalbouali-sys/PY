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
            table.append(list(part))  # known characters
    return table


# ==========================================================
# TOTAL COMBINATION CALCULATOR
# ==========================================================
def calculate_total_combinations(min_len, max_len, charset, table):

    # Total number of combinations across all lengths
    total = 0

    # Cache charset size for performance
    charset_size = len(charset)

    # --------------------------------------------------
    # Loop over each possible password length
    # --------------------------------------------------
    for length in range(min_len, max_len + 1):

        # Number of combinations for this specific length
        count = 1

        # ----------------------------------------------
        # For each position in the password
        # ----------------------------------------------
        for pos in range(length):

            # If a mask exists for this position,
            # use the number of allowed characters
            if pos < len(table) and table[pos] is not None:
                count *= len(table[pos])

            # Otherwise, use the full charset
            else:
                count *= charset_size

        # Add this length's combinations to total
        total += count

    # Return final total number of attempts
    return total



import itertools

# ==========================================================
# PASSWORD GENERATOR (POSITIONAL – FIXED)
# ==========================================================
def password_generator(min_len, max_len, charset, table):

    # --------------------------------------------------
    # Loop through each password length
    # --------------------------------------------------
    for length in range(min_len, max_len + 1):

        # --------------------------------------------------
        # Build the allowed character set per position
        # --------------------------------------------------
        position_sets = []

        for pos in range(length):

            # If a mask exists for this position,
            # restrict characters accordingly
            if pos < len(table) and table[pos] is not None:
                position_sets.append(table[pos])

            # Otherwise, allow full charset
            else:
                position_sets.append(charset)

        # --------------------------------------------------
        # Generate all combinations using Cartesian product
        # --------------------------------------------------
        # itertools.product picks one character from each
        # position set, producing tuples 
        for combo in itertools.product(*position_sets):

            # Convert tuple of characters into a string
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
    Coordinates the full brute-force attack using a
    producer-consumer multithreaded architecture.
    """

    # --------------------------------------------------
    # Detect target file type and parse mask table
    # --------------------------------------------------
    file_type = detect_file_type(file_path)
    table = parse_table(table_string)

    # --------------------------------------------------
    # Calculate total number of password combinations
    # (used only for progress reporting)
    # --------------------------------------------------
    total_combinations = calculate_total_combinations(min_len, max_len, charset, table)

    # --------------------------------------------------
    # Shared queue for password distribution
    # --------------------------------------------------
    password_queue = Queue(maxsize=QUEUE_MAX_SIZE)

    # Signals that the producer has finished generating passwords
    producer_done = threading.Event()

    # --------------------------------------------------
    # Thread-safe progress tracking
    # --------------------------------------------------
    tested = 0
    tested_lock = threading.Lock()

    # --------------------------------------------------
    # Shared result container
    # --------------------------------------------------
    result = {"password": None}

    # ==================================================
    # WORKER THREAD FUNCTION
    # ==================================================
    def worker():
        nonlocal tested

        while not stop_flag.is_set():
            try:
                # Retrieve next password candidate
                pwd = password_queue.get(timeout=0.3)

            except Empty:
                # If no more passwords will arrive, exit
                if producer_done.is_set():
                    return
                continue

            # ------------------------------------------
            # Test password based on file type
            # ------------------------------------------
            if file_type == "zip":
                success = test_zip(file_path, pwd)
            elif file_type == "7z":
                success = test_7z(file_path, pwd)
            else:
                success = test_pdf(file_path, pwd)

            # ------------------------------------------
            # Update progress safely
            # ------------------------------------------
            with tested_lock:
                tested += 1
                progress_callback(tested, total_combinations)

            # ------------------------------------------
            # Stop all threads if password is found
            # ------------------------------------------
            if success:
                result["password"] = pwd
                stop_flag.set()

            # Mark queue task as complete
            password_queue.task_done()

    # ==================================================
    # START WORKER THREADS
    # ==================================================
    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    # ==================================================
    # PRODUCER: generate passwords
    # ==================================================
    for pwd in password_generator(min_len, max_len, charset, table):
        if stop_flag.is_set():
            break
        password_queue.put(pwd)

    # Signal no more passwords will be generated
    producer_done.set()

    # Wait for all queued passwords to be processed
    password_queue.join()

    # Return found password or None
    return result["password"]

