from app.modules.social.application.dto.social_dto import (
    CurriculumSocialStatsDTO,
    UserSocialStatsDTO,
)
from app.modules.social.domain.repository.like_repo import ILikeRepository
from app.modules.social.domain.repository.comment_repo import ICommentRepository
from app.modules.social.domain.repository.bookmark_repo import IBookmarkRepository
from app.modules.user.domain.vo.role import RoleVO


class SocialStatsService:
    def __init__(
        self,
        like_repo: ILikeRepository,
        comment_repo: ICommentRepository,
        bookmark_repo: IBookmarkRepository,
    ) -> None:
        self.like_repo: ILikeRepository = like_repo
        self.comment_repo: ICommentRepository = comment_repo
        self.bookmark_repo: IBookmarkRepository = bookmark_repo

    async def get_curriculum_social_stats(
        self,
        curriculum_id: str,
        user_id: str,
        role: RoleVO,
    ) -> CurriculumSocialStatsDTO:
        """커리큘럼 소셜 통계 조회"""
        like_count: int = await self.like_repo.count_by_curriculum(curriculum_id)
        comment_count: int = await self.comment_repo.count_by_curriculum(curriculum_id)
        is_liked: bool = await self.like_repo.exists_by_curriculum_and_user(
            curriculum_id, user_id
        )
        is_bookmarked: bool = await self.bookmark_repo.exists_by_curriculum_and_user(
            curriculum_id, user_id
        )

        return CurriculumSocialStatsDTO(
            curriculum_id=curriculum_id,
            like_count=like_count,
            comment_count=comment_count,
            is_liked_by_user=is_liked,
            is_bookmarked_by_user=is_bookmarked,
        )

    async def get_user_social_stats(
        self,
        user_id: str,
    ) -> UserSocialStatsDTO:
        """사용자 소셜 통계 조회"""
        total_likes_given: int = await self.like_repo.count_by_user(user_id)
        total_comments_written: int = await self.comment_repo.count_by_user(user_id)
        total_bookmarks: int = await self.bookmark_repo.count_by_user(user_id)

        # TODO: 자신의 커리큘럼이 받은 좋아요/댓글 수는 curriculum과 조인해서 계산
        # 현재는 0으로 설정 (추후 구현)
        total_likes_received = 0
        total_comments_received = 0

        return UserSocialStatsDTO(
            user_id=user_id,
            total_likes_given=total_likes_given,
            total_comments_written=total_comments_written,
            total_bookmarks=total_bookmarks,
            total_likes_received=total_likes_received,
            total_comments_received=total_comments_received,
        )
