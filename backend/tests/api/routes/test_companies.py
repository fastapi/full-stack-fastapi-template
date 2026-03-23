from fastapi.testclient import TestClient

from app.core.config import settings

VALID_COMPANY_DATA = {
    "cnpj": "12345678000199",
    "razao_social": "Empresa Teste LTDA",
    "representante_legal": "João da Silva",
    "data_abertura": "2020-01-15",
    "nome_fantasia": "Empresa Teste",
    "porte": "ME",
    "atividade_economica_principal": "62.01-5-01",
    "atividade_economica_secundaria": "62.02-3-00",
    "natureza_juridica": "206-2",
    "logradouro": "Rua das Flores",
    "numero": "100",
    "complemento": "Sala 201",
    "cep": "01001000",
    "bairro": "Centro",
    "municipio": "São Paulo",
    "uf": "SP",
    "endereco_eletronico": "contato@empresa.com.br",
    "telefone_comercial": "1133334444",
    "situacao_cadastral": "Ativa",
    "data_situacao_cadastral": "2020-01-15",
    "cpf_representante_legal": "12345678901",
    "identidade_representante_legal": "123456789",
    "logradouro_representante_legal": "Av. Paulista",
    "numero_representante_legal": "500",
    "complemento_representante_legal": "Apto 10",
    "cep_representante_legal": "01310100",
    "bairro_representante_legal": "Bela Vista",
    "municipio_representante_legal": "São Paulo",
    "uf_representante_legal": "SP",
    "endereco_eletronico_representante_legal": "joao@email.com",
    "telefones_representante_legal": "11999998888",
    "data_nascimento_representante_legal": "1985-06-20",
    "banco_cc_cnpj": "Banco do Brasil",
    "agencia_cc_cnpj": "1234-5",
}


def test_create_company(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/companies/",
        headers=superuser_token_headers,
        json=VALID_COMPANY_DATA,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["cnpj"] == VALID_COMPANY_DATA["cnpj"]
    assert content["razao_social"] == VALID_COMPANY_DATA["razao_social"]
    assert content["representante_legal"] == VALID_COMPANY_DATA["representante_legal"]
    assert content["nome_fantasia"] == VALID_COMPANY_DATA["nome_fantasia"]
    assert content["porte"] == VALID_COMPANY_DATA["porte"]
    assert content["logradouro"] == VALID_COMPANY_DATA["logradouro"]
    assert content["cpf_representante_legal"] == VALID_COMPANY_DATA["cpf_representante_legal"]
    assert content["banco_cc_cnpj"] == VALID_COMPANY_DATA["banco_cc_cnpj"]
    assert content["agencia_cc_cnpj"] == VALID_COMPANY_DATA["agencia_cc_cnpj"]
    assert "id" in content
    assert "created_at" in content


def test_create_company_missing_field(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    incomplete_data = VALID_COMPANY_DATA.copy()
    del incomplete_data["cnpj"]
    response = client.post(
        f"{settings.API_V1_STR}/companies/",
        headers=superuser_token_headers,
        json=incomplete_data,
    )
    assert response.status_code == 422


def test_create_company_duplicate_cnpj(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = VALID_COMPANY_DATA.copy()
    data["cnpj"] = "99999999000100"
    response = client.post(
        f"{settings.API_V1_STR}/companies/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200

    response = client.post(
        f"{settings.API_V1_STR}/companies/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "A company with this CNPJ already exists."
