import os
import threading

from testpass import (
    test_zip, test_7z, test_pdf,
    is_zip_protected, is_7z_protected, is_pdf_protected
)

from word_list_temporary_files import split_wordlist_into_temp_files


# =======================================================
# Select correct password testing function based on file
# extension (ZIP / 7Z / PDF)
# =======================================================
def get_test_function(file_path):
    """
    Returns the correct password testing function
    depending on the file extension.

    Supported:
    - .zip -> test_zip
    - .7z  -> test_7z
    - .pdf -> test_pdf
    """
    ext = file_path.lower()
    if ext.endswith(".zip"):
        return test_zip
    elif ext.endswith(".7z"):
        return test_7z
    elif ext.endswith(".pdf"):
        return test_pdf
    return None


# =======================================================
# Detect whether the target file is password-protected
# =======================================================
def is_file_protected(file_path):
    """
    Checks if the given file is protected by a password.

    Returns:
        True  -> password required
        False -> no password
    """
    ext = file_path.lower()
    if ext.endswith(".zip"):
        return is_zip_protected(file_path)
    elif ext.endswith(".7z"):
        return is_7z_protected(file_path)
    elif ext.endswith(".pdf"):
        return is_pdf_protected(file_path)
    return False


# =======================================================
# MULTI-THREADED WORDLIST CRACKING ENGINE
# (GUI-agnostic but GUI-aware via window events)
# =======================================================
def default_wordlist_crack(
    file_path,
    wordlists,
    test_function,
    window,
    thread_limit=2
):
    """
    Core cracking engine.

    Responsibilities:
    - Split wordlists into temporary files
    - Spawn worker threads
    - Coordinate stopping on success or cancel
    - Report progress to GUI
    - GUARANTEE cleanup of temporary files

    Returns:
        (password, True)  -> if password found
        (None, False)     -> otherwise
    """

    try:
        # Loop over provided wordlists (usually 1)
        for wl_path in wordlists:

            # --------------------------------------------------
            # Split wordlist into N temporary files
            # Each temp file is processed by one thread
            # --------------------------------------------------
            temp_lists = split_wordlist_into_temp_files(
                wl_path,
                num_temp_files=thread_limit
            )

            # --------------------------------------------------
            # Thread coordination primitives
            # --------------------------------------------------
            stop_flag = threading.Event()      # Signals workers to stop
            result = {"password": None}        # Shared result container

            # --------------------------------------------------
            # Count total passwords (for progress calculation)
            # --------------------------------------------------
            total = sum(
                sum(1 for _ in open(p, "r", encoding="utf-8", errors="ignore"))
                for p in temp_lists
            )

            tested = 0  # Number of passwords already tested

            # ==================================================
            # Worker thread function
            # Each thread processes one temp file
            # ==================================================
            def worker(temp_file):
                """
                Reads passwords line-by-line from a temporary file
                and tests them against the protected file.
                """
                with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:

                        # Stop immediately if another thread succeeded
                        if stop_flag.is_set():
                            return

                        password = line.strip()
                        if not password:
                            continue

                        # Debug / console trace (safe to remove later)
                        print(f"[{threading.current_thread().name}] {password}")

                        # Attempt password
                        if test_function(file_path, password):
                            result["password"] = password
                            stop_flag.set()
                            window.write_event_value("-FOUND-", password)
                            return

                        # Notify GUI that one attempt was completed
                        window.write_event_value("-PROGRESS-", 1)

            # --------------------------------------------------
            # Start worker threads
            # --------------------------------------------------
            for temp_file in temp_lists:
                threading.Thread(
                    target=worker,
                    args=(temp_file,),
                    daemon=True
                ).start()

            # ==================================================
            # GUI-controlled event loop
            # ==================================================
            try:
                while not stop_flag.is_set() and tested < total:

                    event, value = window.read(timeout=50)

                    # User cancelled or window closed
                    if event in ("-CANCEL-", None):
                        stop_flag.set()
                        return None, False

                    # Progress update
                    if event == "-PROGRESS-":
                        tested += 1
                        window["-PROG-"].update(
                            int((tested / total) * 100)
                        )

                    # Password found
                    if event == "-FOUND-":
                        stop_flag.set()
                        return value, True

            finally:
                # ==================================================
                # GUARANTEED CLEANUP
                # Runs on success, failure, cancel, or exception
                # ==================================================
                for temp in temp_lists:
                    try:
                        os.remove(temp)
                    except Exception:
                        pass

        # No password found in any wordlist
        return None, False

    except Exception as e:
        print("ERROR in default_wordlist_crack:", e)
        return None, False
