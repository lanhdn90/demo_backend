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