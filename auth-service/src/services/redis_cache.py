from redis.asyncio import Redis


class CacheRedis:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def _object_from_cache(self, obj: str) -> bool:
        data = await self.redis.get(obj)
        return True if data else False

    async def _put_object_to_cache(self, obj: str, time_cache: int = 30):
        await self.redis.set(obj, obj, time_cache)
