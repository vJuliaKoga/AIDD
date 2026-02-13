import hashlib

with open("output.txt", "rb") as f:
    data = f.read()

print(hashlib.sha256(data).hexdigest())
