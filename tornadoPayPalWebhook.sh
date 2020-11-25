mkdir demoCA
mkdir demoCA/newcerts
touch demoCA/index.txt
echo "0010" > demoCA/serial
openssl genrsa -des3 -out server.key 1024
openssl req -new -key server.key -out server.csr
openssl req -new -x509 -keyout ca.key -out ca.crt
openssl ca -in server.csr -out server.crt -cert ca.crt -keyfile ca.key