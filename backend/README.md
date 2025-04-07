# Banco de Dados


### Tickets
- **id**
- **title**
- **description**
- **category** (Suporte, Manutenção, Dúvida)
- **priority** (Baixa, Média, Alta)
- **status** (Aberto, Em andamento, Fechado)
- **user_id**
- **created_at**
- **updated_at**

### Comments
- **id**
- **ticket_id**
- **user_id**
- **comment**
- **created_at**

---

# Endpoints


## GET /tickets
- **Descrição**: Listar todos os tickets (com filtros e paginação).
- **Exemplo de Response**:
{
  "tickets": [
    {
      "id": 1,
      "title": "Erro no sistema",
      "status": "Aberto",
      "priority": "Alta",
      "created_at": "2023-10-01T12:00:00Z"
    },
    {
      "id": 2,
      "title": "Problema com login",
      "status": "Em andamento",
      "priority": "Média",
      "created_at": "2023-10-02T08:30:00Z"
    }
  ],
  "page": 1,
  "total": 2
}

## GET /tickets/{id}
- **Descrição**: Retorna detalhes de um ticket.
- **Exemplo de Response**:
{
  "id": 1,
  "title": "Erro no sistema",
  "description": "Detalhes do erro ocorrido...",
  "category": "Suporte",
  "priority": "Alta",
  "status": "Aberto",
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T12:00:00Z",
  "comments": [
    {
      "id": 1,
      "comment": "Identificado o problema inicial.",
      "created_at": "2023-10-01T12:30:00Z"
    }
  ]
}

## POST /tickets
- **Descrição**: Criar um novo ticket.
- **Request Body**:
{
  "title": "Novo ticket",
  "description": "Detalhes do ticket...",
  "category": "Manutenção",
  "priority": "Média"
}
- **Exemplo de Response**:
{
  "id": 3,
  "title": "Novo ticket",
  "description": "Detalhes do ticket...",
  "category": "Manutenção",
  "priority": "Média",
  "status": "Aberto",
  "created_at": "2023-10-05T10:00:00Z",
  "updated_at": "2023-10-05T10:00:00Z"
}

## PUT /tickets/{id}
- **Descrição**: Atualizar um ticket existente.
- **Request Body**:
{
  "title": "Ticket atualizado",
  "description": "Descrição atualizada...",
  "category": "Suporte",
  "priority": "Alta",
  "status": "Em andamento"
}
- **Exemplo de Response**:
{
  "id": 1,
  "title": "Ticket atualizado",
  "description": "Descrição atualizada...",
  "category": "Suporte",
  "priority": "Alta",
  "status": "Em andamento",
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-05T10:00:00Z"
}

## POST /tickets/{id}/comments
- **Descrição**: Adicionar comentário a um ticket.
- **Request Body**:
{
  "comment": "Comentário adicionado ao ticket."
}
- **Exemplo de Response**:
{
  "id": 5,
  "ticket_id": 1,
  "comment": "Comentário adicionado ao ticket.",
  "created_at": "2023-10-05T10:30:00Z"
}