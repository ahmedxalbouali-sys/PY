import os
import threading

# Password testing functions for each file type
from testpass import (
    test_zip, test_7z, test_pdf,
    is_zip_protected, is_7z_protected, is_pdf_protected
)

# Utility that splits a large wordlist into smaller temporary files
from word_list_temporary_files import split_wordlist_into_temp_files


# =======================================================
# Select the correct password test function
# based on the target file extension
# =======================================================
def get_test_function(file_path):
    ext = file_path.lower()

    if ext.endswith(".zip"):
        return test_zip
    elif ext.endswith(".7z"):
        return test_7z
    elif ext.endswith(".pdf"):
        return test_pdf

    # Unsupported file type
    return None


# =======================================================
# Check whether the file is password-protected
# before attempting to crack it
# =======================================================
def is_file_protected(file_path):
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
#
# - Uses multiple threads to test passwords in parallel
# - Each thread reads from a different temporary wordlist file
# - Stops immediately once the password is found
# =======================================================
def default_wordlist_crack(
    file_path,
    wordlists,
    test_function,
    window,
    thread_limit=2
):

    # Event used to signal all threads to stop when password is found
    stop_flag = threading.Event()

    # Shared result container (dictionary is mutable → thread-safe reference)
    result = {"password": None}

    try:
        # --------------------------------------------------
        # Iterate through each provided wordlist
        # --------------------------------------------------
        for wl_path in wordlists:

            # -----------------------------------------------
            # Split the large wordlist into smaller temp files
            # Each temp file will be handled by one thread
            # -----------------------------------------------
            temp_lists = split_wordlist_into_temp_files(
                wl_path,
                num_temp_files=thread_limit
            )

            # -----------------------------------------------
            # Count total passwords (for progress tracking)
            # -----------------------------------------------
            total = sum(
                sum(1 for _ in open(p, "r", encoding="utf-8", errors="ignore"))
                for p in temp_lists
            )

            # Number of passwords tested so far (shared counter)
            tested = 0

            # Lock to protect concurrent access to "tested"
            tested_lock = threading.Lock()

            # ===============================================
            # Worker thread function
            #
            # Each worker:
            # - Reads passwords from one temp file
            # - Tests each password
            # - Updates shared progress
            # - Stops all threads if password is found
            # ===============================================
            def worker(temp_file):
                nonlocal tested

                # Open assigned temporary wordlist file
                with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:

                        # Stop immediately if another thread succeeded
                        if stop_flag.is_set():
                            return

                        password = line.strip()
                        if not password:
                            continue

                        # Try the password against the file
                        if test_function(file_path, password):
                            # Store result
                            result["password"] = password

                            # Signal all threads to stop
                            stop_flag.set()

                            # Notify GUI that password was found
                            window.write_event_value("-FOUND-", password)
                            return

                        # Safely increment tested counter
                        with tested_lock:
                            tested += 1

                            # Send progress update to GUI
                            window.write_event_value(
                                "-PROGRESS-",
                                tested / total
                            )

            # -----------------------------------------------
            # Start worker threads
            # -----------------------------------------------
            threads = []

            for temp_file in temp_lists:
                t = threading.Thread(
                    target=worker,
                    args=(temp_file,),
                    daemon=True  # Thread stops if main program exits
                )
                t.start()
                threads.append(t)

            # -----------------------------------------------
            # Wait for all threads to finish
            # (either exhausted wordlist or password found)
            # -----------------------------------------------
            for t in threads:
                t.join()

            # -----------------------------------------------
            # Remove temporary wordlist files
            # -----------------------------------------------
            for temp in temp_lists:
                try:
                    os.remove(temp)
                except Exception:
                    pass

            # If password was found, stop processing further wordlists
            if result["password"]:
                return result["password"], True

        # No password found in any wordlist
        return None, False

    except Exception as e:
        print("ERROR in default_wordlist_crack:", e)
        return None, False
