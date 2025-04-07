import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import TicketCategory, TicketPriority, TicketStatus
from app.tests.utils.ticket import create_random_ticket, create_random_comment
from app.tests.utils.user import create_random_user


def test_create_ticket(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Teste para criar um ticket
    """
    data = {
        "title": "Problemas com login", 
        "description": "Não consigo fazer login no sistema",
        "category": TicketCategory.SUPPORT,
        "priority": TicketPriority.MEDIUM,
    }
    response = client.post(
        f"{settings.API_V1_STR}/tickets/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["category"] == data["category"]
    assert content["priority"] == data["priority"]
    assert content["status"] == TicketStatus.OPEN  # Status padrão
    assert "id" in content
    assert "user_id" in content
    assert "created_at" in content
    assert "updated_at" in content


def test_read_ticket(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para ler um ticket específico
    """
    ticket = create_random_ticket(db)
    response = client.get(
        f"{settings.API_V1_STR}/tickets/{ticket.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == ticket.title
    assert content["description"] == ticket.description
    assert content["category"] == ticket.category
    assert content["priority"] == ticket.priority
    assert content["status"] == ticket.status
    assert content["id"] == str(ticket.id)
    assert content["user_id"] == str(ticket.user_id)
    assert "created_at" in content
    assert "updated_at" in content
    assert "comments" in content


def test_read_ticket_with_comments(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para ler um ticket com comentários
    """
    ticket = create_random_ticket(db)
    comment = create_random_comment(db, ticket_id=ticket.id)
    
    response = client.get(
        f"{settings.API_V1_STR}/tickets/{ticket.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["comments"]) == 1
    assert content["comments"][0]["id"] == str(comment.id)
    assert content["comments"][0]["comment"] == comment.comment


def test_read_ticket_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Teste para ler um ticket que não existe
    """
    response = client.get(
        f"{settings.API_V1_STR}/tickets/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Ticket não encontrado"


def test_read_ticket_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para ler um ticket sem permissões suficientes
    """
    # Criar um ticket com um usuário diferente
    other_user = create_random_user(db)
    ticket = create_random_ticket(db, owner_id=other_user.id)
    
    response = client.get(
        f"{settings.API_V1_STR}/tickets/{ticket.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Permissões insuficientes"


def test_read_tickets(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para ler todos os tickets
    """
    create_random_ticket(db)
    create_random_ticket(db)
    response = client.get(
        f"{settings.API_V1_STR}/tickets/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2
    assert "count" in content
    assert "page" in content


def test_filter_tickets_by_category(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para filtrar tickets por categoria
    """
    ticket = create_random_ticket(db)
    category = ticket.category
    
    response = client.get(
        f"{settings.API_V1_STR}/tickets/?category={category}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert all(t["category"] == category for t in content["data"])


def test_update_ticket(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para atualizar um ticket
    """
    ticket = create_random_ticket(db)
    data = {
        "title": "Título atualizado",
        "description": "Descrição atualizada",
        "category": TicketCategory.MAINTENANCE,
        "priority": TicketPriority.HIGH,
        "status": TicketStatus.IN_PROGRESS
    }
    response = client.put(
        f"{settings.API_V1_STR}/tickets/{ticket.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["category"] == data["category"]
    assert content["priority"] == data["priority"]
    assert content["status"] == data["status"]
    assert content["id"] == str(ticket.id)
    assert content["user_id"] == str(ticket.user_id)


def test_update_ticket_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Teste para atualizar um ticket que não existe
    """
    data = {"title": "Título atualizado", "description": "Descrição atualizada"}
    response = client.put(
        f"{settings.API_V1_STR}/tickets/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Ticket não encontrado"


def test_update_ticket_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para atualizar um ticket sem permissões suficientes
    """
    other_user = create_random_user(db)
    ticket = create_random_ticket(db, owner_id=other_user.id)
    data = {"title": "Título atualizado", "description": "Descrição atualizada"}
    
    response = client.put(
        f"{settings.API_V1_STR}/tickets/{ticket.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Permissões insuficientes"


def test_delete_ticket(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para excluir um ticket
    """
    ticket = create_random_ticket(db)
    response = client.delete(
        f"{settings.API_V1_STR}/tickets/{ticket.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Ticket removido com sucesso"


def test_delete_ticket_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Teste para excluir um ticket que não existe
    """
    response = client.delete(
        f"{settings.API_V1_STR}/tickets/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Ticket não encontrado"


def test_delete_ticket_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para excluir um ticket sem permissões suficientes
    """
    other_user = create_random_user(db)
    ticket = create_random_ticket(db, owner_id=other_user.id)
    
    response = client.delete(
        f"{settings.API_V1_STR}/tickets/{ticket.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Permissões insuficientes"


def test_create_comment(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Teste para criar um comentário em um ticket
    """
    ticket = create_random_ticket(db)
    data = {"comment": "Este é um comentário de teste"}
    
    response = client.post(
        f"{settings.API_V1_STR}/tickets/{ticket.id}/comments",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["comment"] == data["comment"]
    assert "id" in content
    assert "created_at" in content


def test_create_comment_ticket_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Teste para criar um comentário em um ticket que não existe
    """
    data = {"comment": "Este é um comentário de teste"}
    
    response = client.post(
        f"{settings.API_V1_STR}/tickets/{uuid.uuid4()}/comments",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Ticket não encontrado"
