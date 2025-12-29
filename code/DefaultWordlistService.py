import os
import threading

from testpass import (
    test_zip, test_7z, test_pdf,
    is_zip_protected, is_7z_protected, is_pdf_protected
)

from word_list_temporary_files import split_wordlist_into_temp_files


# -------------------------------------------------------
# Detect correct testing function based on file extension
# -------------------------------------------------------
def get_test_function(file_path):
    ext = file_path.lower()
    if ext.endswith(".zip"):
        return test_zip
    elif ext.endswith(".7z"):
        return test_7z
    elif ext.endswith(".pdf"):
        return test_pdf
    return None


# -------------------------------------------------------
# Detect if the file is protected or not
# -------------------------------------------------------
def is_file_protected(file_path):
    ext = file_path.lower()
    if ext.endswith(".zip"):
        return is_zip_protected(file_path)
    elif ext.endswith(".7z"):
        return is_7z_protected(file_path)
    elif ext.endswith(".pdf"):
        return is_pdf_protected(file_path)
    return False


# -------------------------------------------------------
# MULTI-THREADED WORDLIST CRACK (GUI-AGNOSTIC)
# -------------------------------------------------------
def default_wordlist_crack(
    file_path,
    wordlists,
    test_function,
    window,
    thread_limit=2
):
    try:
        for wl_path in wordlists:

            temp_lists = split_wordlist_into_temp_files(
                wl_path, num_temp_files=thread_limit
            )

            stop_flag = threading.Event()
            result = {"password": None}

            total = sum(
                sum(1 for _ in open(p, "r", encoding="utf-8", errors="ignore"))
                for p in temp_lists
            )

            tested = 0

            # ----------------------------
            # worker thread
            # ----------------------------
            def worker(temp_file):
                with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if stop_flag.is_set():
                            return

                        password = line.strip()
                        if not password:
                            continue

                        print(f"[{threading.current_thread().name}] {password}")

                        if test_function(file_path, password):
                            result["password"] = password
                            stop_flag.set()
                            window.write_event_value("-FOUND-", password)
                            return

                        window.write_event_value("-PROGRESS-", 1)

            # start threads
            for temp_file in temp_lists:
                threading.Thread(
                    target=worker,
                    args=(temp_file,),
                    daemon=True
                ).start()

            # ----------------------------
            # GUI-controlled wait loop
            # ----------------------------
            while not stop_flag.is_set() and tested < total:
                event, value = window.read(timeout=50)

                if event in ("-CANCEL-", None):
                    stop_flag.set()
                    return None, False

                if event == "-PROGRESS-":
                    tested += 1
                    window["-PROG-"].update(int((tested / total) * 1000))

                if event == "-FOUND-":
                    stop_flag.set()
                    return value, True

            # cleanup temp files
            for temp in temp_lists:
                try:
                    os.remove(temp)
                except:
                    pass

        return None, False

    except Exception as e:
        print("ERROR:", e)
        return None, False