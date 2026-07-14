#import bcrypt function gor password hashing
import bcrypt

#a function to generate the hash passord using bcrypt library
def generate_hash_password(password):
    #convert the password from string to bytes
    password_bytes = password.encode('utf-8')
    #Generate a random salt 
    salt =  bcrypt.gensalt()
    #hash the password using bcrypt and the generated salt
    hash = bcrypt.hashpw(password_bytes, salt)
    #convert the hash password from bytes to string and  returm it
    return hash.decode('utf-8')

# a function to verify the password comparing the hash password and the password provided by the user
def verify_password(password, hashed_password):
    #convert the password from string to bytes
    password_bytes = password.encode('utf-8')
    #convert the hashed password from string to bytes
    hashed_password_bytes = hashed_password.encode('utf-8')
    #verify the password using bcrypt and the hashed password
    is_valid = bcrypt.checkpw(password_bytes, hashed_password_bytes)
    return is_valid