from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    email: EmailStr
    password: str
    cpf: int


class UserSchemaPublic(BaseModel):
    email: EmailStr
    id: int


class UserList(BaseModel):
    users: list[UserSchemaPublic]


class UserUpdate(BaseModel):
    password: str
