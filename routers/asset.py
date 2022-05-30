from typing import Any, Dict, List, Optional
from unicodedata import name
from fastapi import APIRouter, Depends
from numpy import int64, number
from pydantic import BaseModel
from fastapi.security import APIKeyHeader
import pandas
from tb_controller_api import TbControllerApis

router = APIRouter()
token = APIKeyHeader(name="token")


class ObjectId(BaseModel):
    id: str
    entityType: str

class Asset(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = None
    label: Optional[str] = None
    # tenantId: ObjectId
    # customerId: ObjectId
    # createdTime: int
    # additionalInfo: Dict[Any,Any]

class Assets(BaseModel):
    total_pages: int
    total_elements: int
    has_next: bool
    data: List[Asset]

# Get asset tenant

# eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJsYW5oZG45MEBnbWFpbC5jb20iLCJzY29wZXMiOlsiVEVOQU5UX0FETUlOIl0sInVzZXJJZCI6IjNiNzUyNTIwLWRiZDYtMTFlYy04ZDQzLWIzMjVmNGEzMmQxYiIsImZpcnN0TmFtZSI6IkxhbmgiLCJsYXN0TmFtZSI6Ikh1eW5oIiwiZW5hYmxlZCI6dHJ1ZSwiaXNQdWJsaWMiOmZhbHNlLCJ0ZW5hbnRJZCI6IjJmOTIxNWIwLWRiZDYtMTFlYy04ZDQzLWIzMjVmNGEzMmQxYiIsImN1c3RvbWVySWQiOiIxMzgxNDAwMC0xZGQyLTExYjItODA4MC04MDgwODA4MDgwODAiLCJpc3MiOiJ0aGluZ3Nib2FyZC5pbyIsImlhdCI6MTY1Mzg5OTI5OSwiZXhwIjoxNjUzOTA4Mjk5fQ.O7GaQMnVWZ2Yph6nD6g9EUA4k1KSK6DS1yWU9Gyk_TXYjmVZys5MO-Uuq08wa6zfWmDXvbLT3NEmS2LTYRLH-Q


@router.get("/api/v1/assets", tags=['Asset'], response_model=Assets)
async def get_assets(page_size: int, page: int, text_search: Optional[str] = None, token: APIKeyHeader = Depends(token)):
    # asset_type = ["Post","Truck","Storage"]
    type = ["Post","Storage","Truck"]
    total_elements = 0
    tb_controller_apis_client = TbControllerApis(token)
    resp = await tb_controller_apis_client.read_tenant_assets(type, text_search, page_size, page)
    data = resp.data["data"]
    print(data)
    # new_data = pandas(resp)
    new_list : List[Asset] = []
    for key in data:
        new_list.append({
            "id": key["id"]["id"],
            "name": key["name"],
            "type": key["type"]
        })
    # return resp
    print(new_list)
    return {
        "total_pages": resp.data["totalPages"],
        "total_elements": resp.data["totalElements"],
        "has_next": resp.data["hasNext"],
        "data": new_list
    }