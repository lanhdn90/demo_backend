from types import NoneType
from typing import Any, Dict, List, Optional
from unicodedata import name
from xml.etree.ElementTree import tostring
from xmlrpc.client import boolean
from fastapi import APIRouter, Depends, HTTPException
from numpy import int64, number
from pydantic import BaseModel
from fastapi.security import APIKeyHeader
import pandas
from sqlalchemy import false, null, true
from tb_controller_api import TbControllerApis
from enum import Enum
import db_api
import utils
import asyncio
import random
import string
router = APIRouter()
token = APIKeyHeader(name="token")


class AssetType(str, Enum):
    POST = "Post"
    STORAGE = "storage"
    TRUCK = "Truck"


class additionalInfo(BaseModel):
    description: str


class NewAsset(BaseModel):
    name: str
    type: str
    label: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


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


class Geometry(BaseModel):
    type: Optional[str] = None
    coordinates: Optional[List[str | None]] = None


class PropertiesAsset(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    descriptions: Optional[str] = None
    phone: Optional[str] = None
    minTemperature: Optional[float] = None
    maxTemperature: Optional[float] = None
    minHumidity: Optional[float] = None
    maxHumidity: Optional[float] = None
    time_limit: Optional[float] = None
    status_door: Optional[bool] = None
    time_open: Optional[int] = None


class AssetInfo(BaseModel):
    type: str
    geometry: Optional[Geometry] = None
    properties: Optional[PropertiesAsset] = None

# Get assets tenant


@router.get("/api/v1/assets", tags=['Asset'], response_model=Assets)
async def get_assets(page_size: int, page: int, text_search: Optional[str] = None, token: APIKeyHeader = Depends(token)):
    user_infor = utils.decode_jwt_token(token)
    if user_infor == False:
        raise HTTPException(401)
    tenant_id = user_infor["tenant_id"]
    print("text_search", text_search)
    resp = db_api.get_asset_parent(tenant_id, page_size, page)
    return resp


# Get Asset info


@router.get("/api/v1/asset/{asset_id}/info", tags=["Asset"], response_model=AssetInfo)
async def get_asset_info(asset_id: str, token: APIKeyHeader = Depends(token)):
    tb_controller_apis_client = TbControllerApis(token)
    resps = await asyncio.gather(
        tb_controller_apis_client.read_asset_by_id(asset_id),
        tb_controller_apis_client.read_attributes(
            {"entity_id": asset_id, "entity_type": "ASSET"}, ""),
        tb_controller_apis_client.read_latest_telemetry(
            {"entity_id": asset_id, "entity_type": "ASSET"}, "status_door_3,status_door_1,status_door_2,status_door_5,status_door_4"),
    )
    for i in resps:
        if i.status != 200:
            raise HTTPException(i.status)
    asset = resps[0].data
    asset_attributes = {i["key"]: i["value"] for i in resps[1].data}
    log = asset_attributes.get('Longitude', None)
    print(log)
    if(asset['type'] == "Post"):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(asset_attributes.get('Longitude', None)), float(asset_attributes.get('Latitude', None))]
            },
            "properties": {
                "id": asset['id']['id'],
                "type": asset['type'],
                "name": asset['name'],
                "address": asset_attributes.get('address', None),
                "descriptions": asset['additionalInfo']['description'],
                "phone": asset_attributes.get('phone', None),
            }
        }
    array_keys = resps[2].data.keys()
    time_array: list[int] = []
    for i in array_keys:
        key = resps[2].data[i][0]['value']
        if(type(key) != NoneType):
            first = key.find("-")
            second = key.rfind("-")
            time = int(key[second + 1: len(key)])
            if(key[first+1: second] == 'true'):
                time_array.append(time)
    time_array.sort(reverse=True)
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [asset_attributes.get('Longitude', None), asset_attributes.get('Latitude', None)]
        },
        "properties": {
            "id": asset['id']['id'],
            "type": asset['type'],
            "name": asset["name"].split("-")[0],
            "address": asset_attributes.get('address', None),
            "descriptions": asset['additionalInfo']['description'] if asset['additionalInfo']['description'] != "" else None,
            "phone": asset_attributes.get('phone', None),
            "minTemperature": asset_attributes.get('minTemperature', None),
            'maxTemperature': asset_attributes.get('maxTemperature', None),
            "minHumidity": asset_attributes.get('minHumidity', None),
            "maxHumidity": asset_attributes.get('maxHumidity', None),
            "time_limit": asset_attributes.get('time_limit', None),
            'status_door': True if len(time_array) != 0 else False,
            "time_open": time_array[0] if len(time_array) != 0 else None
        }
    }

# create Asset


@router.post("/api/v1/asset", tags=["Asset"], response_model=Asset)
async def create_asset(new_asset: NewAsset, token: APIKeyHeader = Depends(token)):
    tb_controller_apis_client = TbControllerApis(token)
    # check name format
    if utils.check_name_format(new_asset.name) == False:
        raise HTTPException(400, "Bad name!")
    # create asset code
    leters = string.ascii_letters
    code = "".join(random.choice(leters) for i in range(16))
    # create asset name
    name = f"{new_asset.name}-{code}"
    # create new asset
    resp = await tb_controller_apis_client.save_asset({
        "name": name,
        "type": new_asset.type,
        "label": new_asset.label,
        "additionalInfo": {
            "description": new_asset.description
        }
    })
    if resp.status != 200:
        raise HTTPException(resp.status)
    asset = resp.data
    # # add asset to asset's parent
    # resp = await tb_controller_apis_client.save_relation({"entity_id": new_asset.parent.entity_id, "entity_type": new_asset.parent.entity_type}, {"entity_id": asset["id"]["id"], "entity_type": "ASSET"})
    # if resp.status != 200:
    #     raise HTTPException(resp.status)
    return {
        "id": asset["id"]["id"],
        "name": asset["name"].split("-")[0],
        "type": asset["type"]
    }
