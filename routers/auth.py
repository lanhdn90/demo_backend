# from http.client import HTTPException
from typing import Optional
from fastapi import Depends, HTTPException

from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.security import APIKeyHeader
from tb_controller_api import TbControllerApis

router = APIRouter()

token = APIKeyHeader(name="token")

class UserPW(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    token: str
    refresh_token: str


class RefreshToken(BaseModel):
    refresh_token: str

class User(BaseModel):
    id: str
    email: str
    authority: str
    created_ts: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    customer_id: str
    name: str
    tenant_id: str
    status: str

class ChangePasswordForm(BaseModel):
    current_password: str
    new_password: str


@router.post("/api/v1/auth/login", response_model=Token, tags=["Auth"])
async def login(user_pw: UserPW):
    tb_controller_apis_client = TbControllerApis("")
    resp = await tb_controller_apis_client.login(username=user_pw.username,
                                                 password=user_pw.password)
    if resp.status != 200:
        raise HTTPException(resp.status)
    return {
        "token": resp.data["token"],
        "refresh_token": resp.data["refreshToken"]
    }

@router.post("/api/v1/auth/token", response_model=Token, tags=["Auth"])
async def refresh_token(refresh_token: RefreshToken):
    tb_controller_apis_client = TbControllerApis("")
    resp = await tb_controller_apis_client.refresh_token(
        refresh_token=refresh_token.refresh_token)
    if resp.status != 200:
        raise HTTPException(resp.status)
    return {
        "token": resp.data["token"],
        "refresh_token": resp.data["refreshToken"]
    }

@router.get("/api/v1/auth/user", response_model=User, tags=["Auth"])
async def get_user(token: APIKeyHeader = Depends(token)):
    tb_controller_apis_client = TbControllerApis(token)
    resp = await tb_controller_apis_client.read_user()
    if resp.status != 200:
        raise HTTPException(resp.status)
    user = resp.data
    status = "enabled"
    additionalInfo = user.get("additionalInfo")
    credentials = (additionalInfo.get("userCredentialsEnabled", None)
                   if additionalInfo != None else None)
    if credentials == None:
        status = "not activated"
    elif credentials == False:
        status = "disabled"

    customer_id = user["customerId"]["id"]
    return {
        "authority": user.get("authority"),
        "created_ts": user.get("createdTime"),
        "customer_id": customer_id,
        "email": user.get("email", None),
        "first_name": user.get("firstName", None),
        "id": user.get("id").get("id"),
        "last_name": user.get("lastName", None),
        "name": user.get("name", None),
        "tenant_id": user.get("tenantId").get("id"),
        "status": status,
    }

@router.put("/api/v1/auth/change_password", tags=["Auth"])
async def change_password(body: ChangePasswordForm, token: APIKeyHeader = Depends(token)):
    tb_controller_apis_client = TbControllerApis(token)
    request_body = {
        "currentPassword": body.current_password,
        "newPassword": body.new_password,
    }
    resp = await tb_controller_apis_client.change_password(request_body)
    if resp.status != 200:
        raise HTTPException(resp.status)
    return "Successfully"