from fastapi import Header

CLIENT_ID_HEADER = "X-Client-Id"


async def get_client_id(x_client_id: str = Header(..., min_length=8, max_length=64)) -> str:
    return x_client_id
