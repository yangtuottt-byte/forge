"""用户相关请求/响应 schema"""

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """注册请求体"""

    email: EmailStr  # pydantic 校验合法邮箱格式
    password: str


class UserOut(BaseModel):
    """用户输出"""

    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 对象构造
    id: int
    email: EmailStr
    role: str


class Token(BaseModel):
    """登录成功返回的令牌"""

    access_token: str
    token_type: str = "bearer"
