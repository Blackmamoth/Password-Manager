from cryptography.fernet import Fernet # Fernet Class to generate public to encrypt and decrypt strings/messages
import sqlite3  # to create a lightweight database to store and manage passwords
import os  # to do commandline stuff(clear screen) and check whether some files exist 
import hashlib  # generate hashes of strings
from getpass import getpass  # to take user input anonymously
import platform # to check what os of computer where file ran in this case

os_name = platform.system() # returns the OS of the computer currently running the file

'''Choose the clear screen command bases on the OS'''
if os_name == 'Windows':
    clear = 'cls'
else:
    clear = 'clear'



def hash_string(string):
    '''return hash of the string passed with SHA512 algorithm'''
    return hashlib.sha512(string.encode('utf-8')).hexdigest()


if not os.path.exists('./passwords.db') or not os.path.exists('./root_pass.txt'):
    '''if the db file and root password file doesn't exist create them
       and create the table to store passwords
       also take root password and save the hash in the root_pass.txt file
    '''
    db = sqlite3.connect('passwords.db')
    cursor = db.cursor() 

    cursor.execute('''CREATE TABLE manager(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        passwd_for TEXT UNIQUE NOT NULL,
        passwd TEXT NOT NULL
    );''')

    root_pass = getpass("Set your root password: ")
    root_pass = hash_string(root_pass)
    with open('root_pass.txt', 'w', encoding='utf-8') as passwd_file:
        passwd_file.write(root_pass)
    '''Also generate the public to encrypt and decrypt strings/messages
       and store it in the file to use it the next time we run the program'''
    key = Fernet.generate_key()
    with open('fernet_key.txt', 'w', encoding='utf-8') as key_file:
        key_file.write(key.decode('utf-8'))
else:
    '''if the files do exist, connect to the database and create a cursor object using cursor() method'''
    db = sqlite3.connect('passwords.db')  
    cursor = db.cursor()  
    '''read from the root_pass.txt file the root password to use in the program further'''
    with open('root_pass.txt', 'r', encoding='utf-8') as passwd_file:
        root_pass = passwd_file.readline()
    '''read from the fernet_key.txt file the public key to encrypt and decrypt the messages with the same key everytime the function runs'''
    with open('fernet_key.txt', 'r', encoding='utf-8') as key_file:
        key = key_file.readline().encode('utf-8')

# instance the Fernet class with the key (generated fresh or read from the file)
fernet = Fernet(key)  


def show_help():
    '''A function to show all the actions a user can perform'''
    print("1. Insert a new record")
    print("2. Show all records")
    print("3. Change one of the current passwords")
    print("4. Delete ont of the current password")
    print("5. Show help")
    print("6. Exit")



def encrypt_string(string):
    '''A function that encrypts the string provided using the public key'''
    return fernet.encrypt(string.encode('utf-8')).decode('utf-8')


def decrypt_string(string):
    '''A function that decrypts the string provided using the public key'''
    return fernet.decrypt(string.encode('utf-8')).decode('utf-8')


class PasswordManager:

    def __init__(self, passwd_for, passwd):
        '''Take password and the website/app the password is for and encrypt the password'''
        self.passwd_for = passwd_for
        self.passwd = encrypt_string(passwd)

    def validate(self):
        '''A function that returns True if length passwd_for and passwd is not zero else returns False'''
        if self.passwd_for and self.passwd:
            return True
        return False

    def insert(self):
        '''Insert passwd_for and password into the database and commit to the database to save permanently'''
        query = f"INSERT INTO manager(passwd_for, passwd) VALUES ('{self.passwd_for}', '{self.passwd}');"
        cursor.execute(query)
        db.commit()

    @staticmethod
    def show_passwds(root_passwd):
        '''A function that takes the root password as and argument
           from the user and if it matches with root password read
           from the root_pass.txt perform the further queries to
           show all the password also decrypt the password while
           showing to the user'''
        if hash_string(root_passwd) == root_pass:
            query = "SELECT passwd_for, passwd FROM manager;"
            cursor.execute(query)
            passwds = cursor.fetchall()  
            print('Password-For\tPassword\n')
            for passwd in passwds:  
                print(f"{passwd[0]}\t\t{decrypt_string(passwd[1])}")
        else:
            print("Wrong password")

    @staticmethod
    def change_password(passwd_for, old_passwd, new_passwd):
        '''A function that takes the entry for which the password has to be change, the old password, and the new password
           check whether the entry exists for which the password has to be changed.
           If the old_passwd matches with password currently saved in the database perform further queries to change
           that password to the new one'''
        query = f"SELECT passwd FROM manager WHERE passwd_for='{passwd_for}';"
        cursor.execute(query)
        password = cursor.fetchone() 
        if not password == None:  
            if hash_string(old_passwd) == hash_string(decrypt_string(password[0])):
                change_pass_query = f"UPDATE manager SET passwd='{encrypt_string(new_passwd)}' WHERE passwd_for='{passwd_for}'"
                cursor.execute(change_pass_query)
                db.commit()
                print(f"Password updated for {passwd_for}")
            else:
                print(
                    "The password you provided does not match with the current password.")
                print("Please try again and provide the correct password")
        else:
            print(f"Password for {passwd_for} Doesn't exist")
            print("Please check again")
            print("Everything here is case sensitive")

    @staticmethod
    def delete_passwd(passwd_for, root_passwd):
        '''A function that takes the entry for which the password has to be changed and the root password
           to delete an entry/record from the database'''
        if hash_string(root_passwd) == root_pass:
            query = f"DELETE FROM manager WHERE passwd_for='{passwd_for}';"
            cursor.execute(query)
            db.commit()
            print(f"Password deleted for {passwd_for}")
        else:
            print("Wrong root password")

if __name__ == '__main__':
    show_help()
    while True:
        action = int(input("\nSelect between (1-6) to perform an action: "))
        if action == 1:
            os.system(clear)
            pass_for = input("What app/website this password if for: ")
            passwd = getpass(f"Enter your password for {pass_for}: ")
            insert = PasswordManager(passwd_for=pass_for, passwd=passwd)
            if insert.validate():
                insert.insert()
            else:
                print("Length of your password-for/password is 0")
                print("Please provide correct inputs")
        elif action == 2:
            os.system(clear)
            root = getpass("Enter your root password to see all records: ")
            PasswordManager.show_passwds(root)
        elif action == 3:
            os.system(clear)
            pass_for = input("Change password for: ")
            old_pass = getpass(f"Enter your old password for {pass_for}: ")
            new_pass = getpass(f"Enter new password for {pass_for}: ")
            PasswordManager.change_password(
                passwd_for=pass_for, old_passwd=old_pass, new_passwd=new_pass)
        elif action == 4:
            os.system(clear)
            del_for = input("Delete password for: ")
            confirm = input(
                f"Are you sure you wanna delete password for {del_for} (y/n): ")  
            if confirm == 'y':
                root = getpass(
                    "Enter your root password to delete this record: ")
                PasswordManager.delete_passwd(del_for, root)
            elif confirm == 'n':
                print("Fine by me")
            else:
                print("All you had to do was choose between (y/n) dammit CJ")
        elif action == 5:
            os.system(clear)  
            show_help()
        elif action == 6:
            os.system(clear)
            exit()
        else:
            print("Please select between 1-5")
            show_help()
