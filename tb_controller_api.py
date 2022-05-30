from typing import Optional
import settings

class Result:
    def __init__(self,status,data) -> None:
        self.status = status
        self.data = data

class TbControllerApis:
    def __init__(self,token) -> None:
        self.base_path = settings.CORE_URL
        self.headers = {
            "X-Authorization": "Bearer " + token,
            "Accept": "*/*",
            "Content-Type": "application/json",
        }
    async def login(self, username, password):
        resource_path = "/auth/login"
        body = {"username": username, "password": password}
        print(body)
        async with settings.http_client.post(
                url=f"{self.base_path}{resource_path}", json=body) as resp:
            try:
                result = Result(resp.status, await resp.json())
            except:
                result = Result(resp.status, None)
            return result

    async def refresh_token(self, refresh_token):
        resource_path = "/auth/token"
        body = {"refreshToken": refresh_token}
        async with settings.http_client.post(
                url=f"{self.base_path}{resource_path}", json=body) as resp:
            try:
                result = Result(resp.status, await resp.json())
            except:
                result = Result(resp.status, None)
            return result

    async def read_user(self):
        resource_path = "/auth/user"
        async with settings.http_client.get(
                url=f"{self.base_path}{resource_path}",
                headers=self.headers) as resp:
            try:
                result = Result(resp.status, await resp.json())
            except:
                result = Result(resp.status, None)
            return result

    async def change_password(self, body):
        resource_path = "/auth/changePassword"
        async with settings.http_client.post(
                url=f"{self.base_path}{resource_path}",
                headers=self.headers,
                json=body) as resp:
            try:
                result = Result(resp.status, await resp.text())
            except:
                result = Result(resp.status, None)
            return result

    async def read_tenant_assets(
        self,
        type,
        text_search,
        page_size,
        page
    ):
        resource_path = f"/tenant/assets"
        params = {
            "pageSize": page_size,
            "page": page,
            "type": type,
            "textSearch": text_search,
        }
        null_params = []
        for key in params:
            if params[key] == None:
                null_params.append(key)
        for key in null_params:
            params.pop(key)     
        async with settings.http_client.get(
                url=f"{self.base_path}{resource_path}",
                headers=self.headers,
                params=params) as resp:
            try:
                result = Result(resp.status, await resp.json())
            except:
                result = Result(resp.status, None)
            return result