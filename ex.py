import hmac
import hashlib
import base64

client_id = "777bu3d8dircc38c5phqr1feui"
client_secret = "taa67dmqlrtugqdlog021s1vogv7dp3m8159ln164qu5oclao8s"  # Replace with actual secret
username = "kusuma"

message = username + client_id
digest = hmac.new(client_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
secret_hash = base64.b64encode(digest).decode()

print(secret_hash)
