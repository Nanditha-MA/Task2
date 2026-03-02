from pydantic import BaseModel, EmailStr, field_validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

    @field_validator("email")
    @classmethod
    def gmail_only(cls, v):
        if not v.endswith("@gmail.com"):
            raise ValueError("Email must end with @gmail.com")
        return v

    @field_validator("password")
    @classmethod
    def strong_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain special character")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str