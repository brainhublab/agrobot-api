### Creating Broker Certificates and keys:

!!! DON'T CHANGE OUTPUT FILE NAMES OR SYSTEM WILL NOT RECOGNIZE THEM !!!
This Certificates will be generate when run startup.py file. Program will ask to fill in parameters for network and servers.

## 1. Create a CA key pair  
#       cmd:
        `openssl genrsa -des3 -out ca.key 2048`

## 2. Create CA certificate and use the CA key from step 1 to sign it.
#       cmd:
        `openssl req -new -x509 -days 1826 -key ca.key -out ca.crt`

## 3. Create a broker key pair don’t password protect.
#       cmd:
        `openssl genrsa -out server.key 2048`

## 4. Create a broker certificate request using key from step 3
#       cmd:
        `openssl req -new -out server.csr -key server.key`

## 5. Use the CA certificate to sign the broker certificate request from step 4.
#       cmd:
        `openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360`
