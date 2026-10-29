import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.item import create_random_item


def test_create_item(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Foo", "description": "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert "id" in content
    assert "owner_id" in content


def test_create_item_empty_title(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "", "description": "测试空标题"}
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    # print(response.json())
    assert response.status_code == 422


def test_create_item_missing_title(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"description": "测试缺少标题"}
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    # print(response.json())
    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(
        error["loc"] == ["body", "title"] and error["type"] == "missing"
        for error in errors
    )


def test_read_item(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == item.title
    assert content["description"] == item.description
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


def test_read_items_search_no_match(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    created = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json={"title": "买牛奶"},
    )
    assert created.status_code == 200

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        params={"q": uuid.uuid4().hex},
    )

    assert response.status_code == 200
    content = response.json()
    assert content["data"] == []
    assert content["count"] == 0


def test_read_items_search_ignores_case(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    keyword = f"Hello{uuid.uuid4().hex}"

    created = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json={"title": f"学习 {keyword.upper()}"},
    )
    assert created.status_code == 200
    created_id = created.json()["id"]

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        params={"q": keyword.lower()},
    )

    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert [item["id"] for item in content["data"]] == [created_id]


@pytest.mark.parametrize(
    "search_params",
    [
        {},
        {"q": ""},
        {"q": "   "},
    ],
)
def test_read_items_empty_search(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    search_params: dict[str, str],
) -> None:
    expected_ids = set()

    # 为当前普通用户准备两条数据
    for title in ("学习 Python", "买牛奶"):
        created = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=normal_user_token_headers,
            json={"title": title},
        )
        assert created.status_code == 200
        expected_ids.add(created.json()["id"])

    # 不搜索时的结果，作为比较基准
    baseline = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        params={"skip": 0, "limit": 100},
    )
    assert baseline.status_code == 200
    baseline_content = baseline.json()

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        params={"skip": 0, "limit": 100, **search_params},
    )

    assert response.status_code == 200
    content = response.json()
    assert content == baseline_content

    baseline_ids = {item["id"] for item in baseline_content["data"]}
    assert expected_ids <= baseline_ids


def test_read_items_search_pagination_count(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    keyword = uuid.uuid4().hex
    matching_ids = set()

    # 创建两条标题匹配的数据
    for number in range(2):
        created = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=superuser_token_headers,
            json={"title": f"{keyword} 第 {number + 1} 条"},
        )
        assert created.status_code == 200
        matching_ids.add(created.json()["id"])

    # 创建一条不匹配的数据，不应计入搜索总数
    other = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json={"title": "买牛奶"},
    )
    assert other.status_code == 200

    returned_ids = []

    # 分别查询第一页和第二页
    for skip in (0, 1):
        response = client.get(
            f"{settings.API_V1_STR}/items/",
            headers=superuser_token_headers,
            params={"q": keyword, "skip": skip, "limit": 1},
        )

        assert response.status_code == 200
        content = response.json()
        assert content["count"] == 2
        assert len(content["data"]) == 1
        returned_ids.append(content["data"][0]["id"])

    assert set(returned_ids) == matching_ids


def test_read_items_search_respects_owner(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    superuser_token_headers: dict[str, str],
) -> None:
    keyword = uuid.uuid4().hex

    # 普通用户创建自己的匹配数据
    own = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        json={"title": f"自己的 {keyword}"},
    )
    assert own.status_code == 200
    own_id = own.json()["id"]

    # 管理员创建另一条同样匹配的数据
    other = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json={"title": f"别人的 {keyword}"},
    )
    assert other.status_code == 200

    # 普通用户搜索，只应看到自己的那条
    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=normal_user_token_headers,
        params={"q": keyword},
    )

    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert [item["id"] for item in content["data"]] == [own_id]


def test_read_items_search_by_title(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    keyword = uuid.uuid4().hex

    # 创建标题匹配的数据
    matching = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json={"title": f"学习 {keyword}"},
    )
    assert matching.status_code == 200
    matching_id = matching.json()["id"]

    # 创建标题不匹配、但描述包含关键词的数据
    other = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json={"title": "买牛奶", "description": keyword},
    )
    assert other.status_code == 200

    # 按标题关键词搜索
    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        params={"q": keyword},
    )

    assert response.status_code == 200
    content = response.json()
    assert content["count"] == 1
    assert [item["id"] for item in content["data"]] == [matching_id]


@pytest.mark.parametrize(
    "params",
    [
        {"skip": -1},
        {"limit": 0},
        {"limit": 101},
    ],
)
def test_read_items_invalid_pagination(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    params: dict[str, int],
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        params=params,
    )
    assert response.status_code == 422


@pytest.mark.parametrize("limit", [1, 100])
def test_read_items_valid_limit(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
    limit: int,
) -> None:
    create_random_item(db)
    create_random_item(db)

    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        params={"skip": 0, "limit": limit},
    )

    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) == min(limit, content["count"])


def test_read_item_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_read_item_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_items(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_item(db)
    create_random_item(db)
    response = client.get(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_item(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["id"] == str(item.id)
    assert content["owner_id"] == str(item.owner_id)


def test_update_item_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_update_item_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    data = {"title": "Updated title", "description": "Updated description"}
    response = client.put(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_item(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Item deleted successfully"


def test_delete_item_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_delete_item_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    item = create_random_item(db)
    response = client.delete(
        f"{settings.API_V1_STR}/items/{item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
