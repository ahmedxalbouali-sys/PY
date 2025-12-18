import pyzipper
import pikepdf
import py7zr

#   CONFIGURATION
correct_password = "test123"
wrong_password = "wrongpass123"

zip_file = "New folder (3).zip"
pdf_file = "Rapport_23_24_VF_protected.pdf"
seven_zip_file = "New folder (4).7z"



#   ZIP TEST (pyzipper)
def test_zip(path, pwd):
    """
    - Attempts to extract the ZIP file using the given password
    - Returns:
    ---> True if the password is correct
    ---> False if the password is wrong or extraction fails
    """
    try:
        # we retrieve the archive from the path
        with pyzipper.AESZipFile(path) as zf: # modern Zip Archives use AES encryption
            zf.extractall(pwd=pwd.encode()) #the password should be encoded to byte code
        return True
    except:
        return False


print("\n========== ZIP TEST ==========\n")

print("Wrong password:", wrong_password)
print("Result:", "Correct!" if test_zip(zip_file, wrong_password) else "Wrong password")

print("\nCorrect password:", correct_password)
print("Result:", "Correct!" if test_zip(zip_file, correct_password) else "Wrong password")



#   7Z TEST (py7zr)
def test_7z(path, pwd):
    """
    - Attempts to extract the 7z file using the given password
    - Returns:
    ---> True if the password is correct
    ---> False if the password is wrong or extraction fails
    """
    try:
        with py7zr.SevenZipFile(path, mode='r', password=pwd) as archive:
            archive.extractall()
        return True
    except:
        return False

# for test
print("\n========== 7Z TEST ==========\n")

print("Wrong password:", wrong_password)
print("Result:", "Correct!" if test_7z(seven_zip_file, wrong_password) else "Wrong password")

print("\nCorrect password:", correct_password)
print("Result:", "Correct!" if test_7z(seven_zip_file, correct_password) else "Wrong password")



#   PDF TEST (pikepdf)
def test_pdf(path, pwd):
    """
    - Attempts to open the PDF using the given password
    - Returns:
    ---> True if the password is correct
    ---> False if the password is wrong or extraction fails
    """
    try:
        #takes password as input and handles it internally
        with pikepdf.open(path, password=pwd):
            pass
        return True
    except pikepdf.PasswordError:
        return False
    except:
        return False


print("\n========== PDF TEST ==========\n")

print("Wrong password:", wrong_password)
print("Result:", "Correct!" if test_pdf(pdf_file, wrong_password) else "Wrong password")

print("\nCorrect password:", correct_password)
print("Result:", "Correct!" if test_pdf(pdf_file, correct_password) else "Wrong password")


print("\n===============================")
print("TESTING COMPLETE")
print("===============================\n")