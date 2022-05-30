from http.client import HTTPException
from typing import Any, Dict, List, Optional
from unicodedata import name
from fastapi import APIRouter, Depends
from numpy import int64, number
from pydantic import BaseModel
from fastapi.security import APIKeyHeader
import pandas
from tb_controller_api import TbControllerApis
import db_api
import utils
router = APIRouter()
token = APIKeyHeader(name="token")


class ObjectId(BaseModel):
    id: str
    entityType: str


class ObjectAsset(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    label: Optional[str] = None

class Asset(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    label: Optional[str] = None
    children: Optional[List[ObjectAsset]] = None


class Assets(BaseModel):
    total_pages: int
    total_elements: int
    has_next: bool
    data: List[Asset]

# Get assets tenant
@router.get("/api/v1/assets", tags=['Asset'], response_model=Assets)
async def get_assets(page_size: int, page: int, text_search: Optional[str] = None, token: APIKeyHeader = Depends(token)):
    user_infor = utils.decode_jwt_token(token)
    if user_infor == False:
        raise HTTPException(401)
    tenant_id = user_infor["tenant_id"]
    resp = db_api.get_asset_parent(tenant_id,page_size,page)
    return resp