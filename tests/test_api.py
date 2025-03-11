import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from main import app
from app.database import engine
from app.models import Base


# Фикстура для инициализации БД перед каждым тестом
@pytest_asyncio.fixture(scope="function", autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# Фикстура для клиента FastAPI
@pytest.fixture(scope="function")
def client():
    with TestClient(app) as client:
        yield client


# Фикстура для создания пользователя и получения токена
@pytest_asyncio.fixture(scope="function")
async def user_with_token(client: TestClient):
    user_data = {"username": "testuser", "password": "testpassword"}

    # Регистрируем пользователя
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200

    # Логинимся и получаем токен
    response = client.post("/auth/login", json=user_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"token": token}


# Фикстура для создания подразделения
@pytest_asyncio.fixture(scope="function")
async def create_branch(client: TestClient, user_with_token):
    branch_data = {"name": "ВДВ"}
    token = user_with_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/branches/", json=branch_data, headers=headers)
    assert response.status_code == 201

    return response.json()


# Тест для создания подразделения
@pytest.mark.asyncio
async def test_create_branch(client: TestClient, user_with_token):
    branch_data = {"name": "ВДВ"}
    token = user_with_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/branches/", json=branch_data, headers=headers)
    assert response.status_code == 201
    assert "id" in response.json()  # Проверяем, что ID возвращается


# Тест для получения списка подразделений
@pytest.mark.asyncio
async def test_get_branches(client: TestClient, create_branch):
    response = client.get("/branches/")
    assert response.status_code == 200


# Тест для получения подразделения по ID
@pytest.mark.asyncio
async def test_get_branch_by_id(client: TestClient, create_branch):
    branch = create_branch  # Ждём выполнения фикстуры
    branch_id = branch["id"]  # Получаем ID созданного подразделения

    response = client.get(f"/branches/{branch_id}")
    assert response.status_code == 200


# Тест для редактирования подразделения
@pytest.mark.asyncio
async def test_update_branch(client: TestClient, create_branch, user_with_token):
    branch = create_branch
    branch_id = branch["id"]
    updated_data = {"name": "Воздушно-десантные войска"}
    token = user_with_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(f"/branches/{branch_id}", json=updated_data, headers=headers)
    assert response.status_code == 200


# Тест для удаления подразделения
@pytest.mark.asyncio
async def test_delete_branch(client: TestClient, create_branch, user_with_token):
    branch = create_branch
    branch_id = branch["id"]
    token = user_with_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(f"/branches/{branch_id}", headers=headers)
    assert response.status_code == 204

    # Проверка, что подразделение больше не существует
    response = client.get(f"/branches/{branch_id}")
    assert response.status_code == 404


# Тест для получения ошибок с неавторизованным доступом
@pytest.mark.asyncio
async def test_unauthorized_access(client: TestClient):
    branch_data = {"name": "ВДВ"}

    response = client.post("/branches/", json=branch_data)
    assert response.status_code == 401  # Неавторизованный доступ
