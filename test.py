from passlib.context import CryptContext
from database import AsyncSessionLocal

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


if __name__ == "__main__":
    # Example usage
    password = "my_secure_password"
    hashed = get_password_hash(password)
    print(f"Plain: {password}")
    print(f"Hashed: {hashed}")
