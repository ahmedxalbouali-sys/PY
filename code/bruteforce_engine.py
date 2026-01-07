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
# DEFAULT CONFIGURATION (USED BY GUI)
# ==========================================================
# Charset to use if no mask is provided
DEFAULT_CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"
# Minimum and maximum password length
DEFAULT_MIN_LEN = 4
DEFAULT_MAX_LEN = 8
# Number of parallel threads for brute force
DEFAULT_THREADS = 8

# Maximum size of queue to limit memory usage
# Prevents producer from generating too many passwords ahead of workers
QUEUE_MAX_SIZE = 5000


# ==========================================================
# FILE TYPE DETECTION
# ==========================================================
def detect_file_type(path):
    """
    Detects file type and verifies password protection.

    Returns:
        "zip", "7z", or "pdf"

    Raises:
        ValueError if unsupported file or file is not protected
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
    Converts a mask string into a table for positional constraints.

    Example:
        "a|bc||9" -> [['a'], ['b','c'], None, None, ['9']]
        None means the position is unrestricted (use full charset)

    Args:
        table_string: string with '|' separator per position

    Returns:
        List of lists or None per position
    """
    if not table_string:
        return []

    table = []
    for part in table_string.split("|"):
        table.append(list(part) if part else None)

    return table


# ==========================================================
# TOTAL COMBINATION COUNT (FOR PROGRESS)
# ==========================================================
def calculate_total_combinations(min_len, max_len, charset, table):
    """
    Calculates the total number of passwords that will be attempted.

    Used for:
    - Progress reporting
    - Estimating runtime

    Args:
        min_len: minimum password length
        max_len: maximum password length
        charset: full character set
        table: positional constraints (from parse_table)

    Returns:
        Total number of password combinations
    """
    total = 0
    charset_len = len(charset)

    for length in range(min_len, max_len + 1):
        count = 1
        for pos in range(length):
            # If mask specifies allowed characters for this position, use it
            if pos < len(table) and table[pos] is not None:
                count *= len(table[pos])
            else:
                # Otherwise use full charset
                count *= charset_len
        total += count

    return total


# ==========================================================
# PASSWORD GENERATOR (LAZY, MEMORY SAFE)
# ==========================================================
def password_generator(min_len, max_len, charset, table):
    """
    Lazily generates passwords without storing them all in memory.

    Args:
        min_len: minimum password length
        max_len: maximum password length
        charset: character set for unrestricted positions
        table: positional constraints (None or list of allowed chars)

    Yields:
        Next password candidate as a string
    """
    for length in range(min_len, max_len + 1):
        position_sets = []

        # Determine allowed characters for each position
        for pos in range(length):
            if pos < len(table) and table[pos] is not None:
                position_sets.append(table[pos])
            else:
                position_sets.append(charset)

        # Produce all combinations for this length
        for combo in itertools.product(*position_sets):
            yield "".join(combo)


# ==========================================================
# MAIN BRUTE FORCE ENGINE
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
    Main brute-force engine.

    Features:
    - Thread-safe
    - No GUI freeze (can be called from GUI thread safely)
    - Properly responds to stop_flag
    - Memory efficient: generates passwords lazily

    Args:
        file_path: target file
        min_len, max_len: password length range
        charset: characters to use
        table_string: optional mask string
        thread_count: number of worker threads
        progress_callback: function(done, total) for GUI updates
        stop_flag: threading.Event to allow clean cancellation

    Returns:
        Found password string or None if not found
    """

    # --------------------------------------------------
    # Setup
    # --------------------------------------------------
    file_type = detect_file_type(file_path)  # Validate file type and protection
    table = parse_table(table_string)       # Parse optional mask

    total_combinations = calculate_total_combinations(
        min_len, max_len, charset, table
    )

    password_queue = Queue(maxsize=QUEUE_MAX_SIZE)  # Thread-safe queue
    producer_done = threading.Event()              # Signals producer finished

    tested = 0
    tested_lock = threading.Lock()  # Protect shared counter

    result = {"password": None}     # Shared result container


    # ==================================================
    # WORKER THREAD
    # ==================================================
    def worker():
        """
        Worker thread: consumes passwords from the queue and tests them.
        Stops when stop_flag is set AND queue is empty.
        """
        nonlocal tested

        while True:
            # Exit condition: stop requested AND nothing left to process
            if stop_flag.is_set() and password_queue.empty():
                return

            try:
                pwd = password_queue.get(timeout=0.2)
            except Empty:
                # Queue is temporarily empty; check if producer finished
                if producer_done.is_set():
                    return
                continue

            try:
                # Test password depending on file type
                if file_type == "zip":
                    success = test_zip(file_path, pwd)
                elif file_type == "7z":
                    success = test_7z(file_path, pwd)
                else:
                    success = test_pdf(file_path, pwd)

                # Update progress
                with tested_lock:
                    tested += 1
                    progress_callback(tested, total_combinations)

                # Stop immediately if password found
                if success:
                    result["password"] = pwd
                    stop_flag.set()

            finally:
                # Always mark task done to release queue slot
                password_queue.task_done()


    # ==================================================
    # START WORKERS
    # ==================================================
    for _ in range(thread_count):
        threading.Thread(
            target=worker,
            daemon=True
        ).start()


    # ==================================================
    # PRODUCER (MAIN THREAD)
    # ==================================================
    for pwd in password_generator(min_len, max_len, charset, table):
        if stop_flag.is_set():
            break  # Stop producing if cancelled

        # Wait until a slot is available in the queue
        while True:
            try:
                password_queue.put(pwd, timeout=0.2)
                break
            except:
                if stop_flag.is_set():
                    break

    producer_done.set()  # Signal workers that production is finished

    # Wait for all workers to finish
    password_queue.join()

    return result["password"]
