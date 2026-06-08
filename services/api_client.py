import aiohttp
from database import get_setting

async def send_call_api(number: str, limit: int) -> dict:
    api_url = get_setting('api_url', 'https://rakabro.top/api.php')
    api_key = get_setting('api_key', 'Extremeuser')
    params = {"key": api_key, "number": number, "limit": limit}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json(content_type=None)
                return data
        except Exception as e:
            return {"error": str(e)}
