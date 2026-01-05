import os
import threading

from testpass import (
    test_zip, test_7z, test_pdf,
    is_zip_protected, is_7z_protected, is_pdf_protected
)

from word_list_temporary_files import split_wordlist_into_temp_files


# =======================================================
# Select correct password testing function
# =======================================================
def get_test_function(file_path):
    ext = file_path.lower()
    if ext.endswith(".zip"):
        return test_zip
    elif ext.endswith(".7z"):
        return test_7z
    elif ext.endswith(".pdf"):
        return test_pdf
    return None


# =======================================================
# Detect whether file is password-protected
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
# MULTI-THREADED WORDLIST CRACKING ENGINE (FIXED)
# =======================================================
def default_wordlist_crack(
    file_path,
    wordlists,
    test_function,
    window,
    thread_limit=2
):
    """
    Thread-safe cracking engine.

    IMPORTANT:
    - NEVER calls window.read()
    - Worker threads only emit events
    - GUI owns the event loop
    """

    stop_flag = threading.Event()
    result = {"password": None}

    try:
        for wl_path in wordlists:

            # -----------------------------------------------
            # Split wordlist into temp files
            # -----------------------------------------------
            temp_lists = split_wordlist_into_temp_files(
                wl_path,
                num_temp_files=thread_limit
            )

            # -----------------------------------------------
            # Count total passwords
            # -----------------------------------------------
            total = sum(
                sum(1 for _ in open(p, "r", encoding="utf-8", errors="ignore"))
                for p in temp_lists
            )

            tested = 0
            tested_lock = threading.Lock()

            # ===============================================
            # Worker thread
            # ===============================================
            def worker(temp_file):
                nonlocal tested

                with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:

                        if stop_flag.is_set():
                            return

                        password = line.strip()
                        if not password:
                            continue

                        if test_function(file_path, password):
                            result["password"] = password
                            stop_flag.set()
                            window.write_event_value("-FOUND-", password)
                            return

                        with tested_lock:
                            tested += 1
                            window.write_event_value("-PROGRESS-", tested / total)

            # -----------------------------------------------
            # Start threads
            # -----------------------------------------------
            threads = []
            for temp_file in temp_lists:
                t = threading.Thread(
                    target=worker,
                    args=(temp_file,),
                    daemon=True
                )
                t.start()
                threads.append(t)

            # -----------------------------------------------
            # Wait for completion
            # -----------------------------------------------
            for t in threads:
                t.join()

            # -----------------------------------------------
            # Cleanup temp files
            # -----------------------------------------------
            for temp in temp_lists:
                try:
                    os.remove(temp)
                except Exception:
                    pass

            if result["password"]:
                return result["password"], True

        return None, False

    except Exception as e:
        print("ERROR in default_wordlist_crack:", e)
        return None, False
