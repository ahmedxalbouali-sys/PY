import os
import tempfile
from more_itertools import chunked


def split_wordlist_into_temp_files(wordlist_path: str,num_temp_files: int = 5):
    """
    Splits a wordlist into multiple temporary files with approximately the same number of passwords.
    PARAMETERS:
    wordlist_path : str
        Path to the original wordlist file.

    num_temp_files : int (default = 5)
        Number of temporary files to create.

    RETURNS:
    list[str]
        A list of file paths for the created temporary files.
    """

    # 1. Basic validation
    if not os.path.isfile(wordlist_path):
        raise FileNotFoundError("Wordlist file does not exist")
    if num_temp_files <= 0:
        raise ValueError("Number of temporary files must be >= 1")

    # 2. Read the wordlist safely
    with open(wordlist_path, "r") as f:
        passwords = [line.strip() for line in f if line.strip()]
    total_passwords = len(passwords)
    if total_passwords == 0:
        raise ValueError("Wordlist is empty")

    # 3. Calculate chunk size
    chunk_size = total_passwords // num_temp_files
    # If division is not perfect, add 1 to avoid losing passwords in last chunk Ensure chunk size is at least 1
    if total_passwords % num_temp_files != 0:
        chunk_size += 1

    # 4. Split the wordlist into chunks
    chunks = list(chunked(passwords, chunk_size))

    # 5. Create temporary files
    temp_files = []
    for index, chunk in enumerate(chunks):
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            encoding="utf-8",
            prefix=f"wordlist_part_{index}_",
            suffix=".txt"
        )

        # Write passwords into the temp file
        for password in chunk:
            temp_file.write(password + "\n")

        temp_file.close()

        # Store path for later use
        temp_files.append(temp_file.name)


    # 6. Return list of temp file paths
    return temp_files


# Example usage
#temp_lists = split_wordlist_into_temp_files(
#    wordlist_path="C:\\Users\\ahmed\\Desktop\\New folder (2)\\wordlists\\rockyou.txt",
#    num_temp_files=4
#)

#print("Temporary wordlists created:")
#for path in temp_lists:
#    print(path)