from Crypto.Cipher import AES
import os

global cryptokey
cryptokey = b'W\xdf\xfb\x1dn\xc0\xd3\xe1\xce/\x08P\xe6P\rS\xe7\x07\xa6\xebyHwN,P\x0c\x08\x88\xd8\x9e\xda'
file = 'Hotel.db'
buffer_size = 65536

def decrypt(file):
    input_file = open(file, 'rb')
    output_file = open(file + '(decrypted)', 'wb')

    # Read in the iv
    iv = input_file.read(16)

    # Create the cipher object and encrypt the data
    cipher_encrypt = AES.new(cryptokey, AES.MODE_CFB, iv=iv)
    # Keep reading the file into the buffer, decrypting then writing to the new file
    buffer = input_file.read(buffer_size)
    while len(buffer) > 0:
        decrypted_bytes = cipher_encrypt.decrypt(buffer)
        output_file.write(decrypted_bytes)
        buffer = input_file.read(buffer_size)
    # Close the input and output files
    input_file.close()
    output_file.close()
    os.remove(file)
    os.rename(file + '(decrypted)',file)
    #=========count============
    countfile = open("cryptocount.txt", "r")
    count = int(countfile.read())
    countfile.close()
    count -= 1
    countfile = open("cryptocount.txt", "w")
    countfile.write(str(count))
    countfile.close()
def encrypt(file):
    input_file = open(file, 'rb')
    output_file = open(file + '(encrypted)', 'wb')

    # Create the cipher object and encrypt the data
    cipher_encrypt = AES.new(cryptokey, AES.MODE_CFB)

    # Initially write the iv to the output file
    output_file.write(cipher_encrypt.iv)

    # Keep reading the file into the buffer, encrypting then writing to the new file
    buffer = input_file.read(buffer_size)
    while len(buffer) > 0:
        ciphered_bytes = cipher_encrypt.encrypt(buffer)
        output_file.write(ciphered_bytes)
        buffer = input_file.read(buffer_size)

    # Close the input and output files
    input_file.close()
    output_file.close()
    os.remove(file)
    os.rename(file + '(encrypted)', file)
    # =========count============
    countfile = open("cryptocount.txt", "r")
    count = int(countfile.read())
    countfile.close()
    count += 1
    countfile = open("cryptocount.txt", "w")
    countfile.write(str(count))
    countfile.close()

#    #replace replacement\/
#     X = string
#     Y = number of repetitions
#     replace(substr(quote(zeroblob((Y + 1) / 2)), 3, Y), '0', X)
#     select all the fields by name(not *) to change 1 or 2
#     substr(column, - x, x) to get last x chars
#    c.execute("SELECT u_id, replace(substr(quote(zeroblob((length(u_email) - 11) / 2)), 3, length(u_email)-12), '0', 'X') || substr(u_email, - 12, 12), u_username, u_password, 'XXXX XXXX XXXX ' || substr(u_credit_card, - 4, 4) FROM user;") #proof of concept
