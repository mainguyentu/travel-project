from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    status: str


class UserStatusUpdate(BaseModel):
    status: str


class UserRoleUpdate(BaseModel):
    role: str
