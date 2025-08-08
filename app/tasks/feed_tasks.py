# from celery import Celery
# from app.modules.feed.infrastructure.repository.feed_repo import FeedRepository
# from app.common.db.database import AsyncSessionLocal

# celery_app = Celery("feed_tasks")

# @celery_app.task
# def refresh_feed_cache():
#     """주기적 피드 캐시 갱신 (예: 매시간 실행)"""
#     async def _refresh():
#         async with AsyncSessionLocal() as session:
#             feed_repo = FeedRepository(session)
#             await feed_repo.warm_up_cache(limit=200)

#     import asyncio
#     asyncio.run(_refresh())

# @celery_app.task
# def cleanup_expired_cache():
#     """만료된 캐시 정리"""
#     # Redis에서 만료된 키들 정리
#     pass
