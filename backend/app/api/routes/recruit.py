import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends

from pydantic import BaseModel

# もとの認証依存をラップする関数（認証スキップ用）
def optional_session_dep(skip_auth: bool = True):
    def dependency():
        if skip_auth:
            return None
        return None
    return Depends(dependency)

def optional_current_user(skip_auth: bool = True):
    def dependency():
        if skip_auth:
            return None
        return None
    return Depends(dependency)


router = APIRouter(prefix="/recruits", tags=["recruits"])



# Todo: 以下要変更
#  -> model{APIに合わせてkeyを指定}
#  -> 各アルゴリズム実装

# ==== 仮のレスポンス用モデル ====
class RecruitSearchResult(BaseModel):
    id: uuid.UUID
    title: str
    company: str
    location: str
    description: str

class RecruitSearchResponse(BaseModel):
    results: List[RecruitSearchResult]

class RecruitFeedback(BaseModel):
    recruit_id: uuid.UUID
    reason: str  # 例: "Not relevant", "Too far", etc.

# ==== APIエンドポイント ====

@router.get("/search", response_model=RecruitSearchResponse)
def fetch_recruits(
    #     session保持してやりたいならここ変えなきゃいけない
    session: Optional[Any] = optional_session_dep(skip_auth=True),
    current_user: Optional[Any] = optional_current_user(skip_auth=True),
) -> Any:

    """
    フロントエンドのフェッチに反応して求人情報を検索
    """


    dummy_data = [
        RecruitSearchResult(
            id=uuid.uuid4(),
            title="Software Engineer",
            company="Example Corp",
            location="Tokyo",
            description="Develop awesome things",
        )
        for _ in range(30)
    ]
    return RecruitSearchResponse(results=dummy_data)

@router.post("/feedback")
def submit_feedback(
    feedback: RecruitFeedback,
    session: Optional[Any] = optional_session_dep(skip_auth=True),
    current_user: Optional[Any] = optional_current_user(skip_auth=True),
) -> Any:
    """
    求人に対するフィードバックを受け取り保存
    """
    print(f"Received feedback: {feedback}")
    return {"message": "Feedback received"}
