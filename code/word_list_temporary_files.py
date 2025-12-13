import os
import tempfile
from more_itertools import divide

def split_wordlist_into_five(wordlist_path):
    """
    Splits a wordlist into 5 temporary files with approximately
    equal number of passwords.

    Args:
        wordlist_path (str): Path to the input wordlist file.

    Returns:
        list[str]: Paths to the 5 generated temporary files.

    how to use:
        temp_paths = split_wordlist_into_five("rockyou.txt")
    """

    # Read all passwords (strip removes newline)
    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        passwords = [line.rstrip("\n") for line in f]

    # Split into 5 almost equal parts
    chunks = list(divide(5, passwords))

    temp_files = []

    # Create 5 temporary files
    for i, chunk in enumerate(chunks, start=1):
        temp_fd, temp_path = tempfile.mkstemp(prefix=f"wordlist_part_{i}_", suffix=".txt")
        temp_files.append(temp_path)

        with os.fdopen(temp_fd, "w", encoding="utf-8") as tmp:
            for pwd in chunk:
                tmp.write(pwd + "\n")

    return temp_files

temp_paths = split_wordlist_into_five("rockyou.txt")

for path in temp_paths:
    print("Created:", path)
