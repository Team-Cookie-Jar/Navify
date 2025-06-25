import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

psw = "Abcd1234"
hash_psw = hash_password(psw)
print(verify_password(psw, "$2b$12$GeE7hcQ2EQGn2QN8I7Ep4OPZCeuFqHQBYJaAho5RsUru38PhbvhTa"))