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

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200

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
    assert "id" in response.json()


# Тест для получения списка подразделений
@pytest.mark.asyncio
async def test_get_branches(client: TestClient, create_branch):
    response = client.get("/branches/")
    assert response.status_code == 200


# Тест для получения подразделения по ID
@pytest.mark.asyncio
async def test_get_branch_by_id(client: TestClient, create_branch):
    branch = create_branch
    branch_id = branch["id"]

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

# Тест для получения ошибок с неавторизованным доступом
@pytest.mark.asyncio
async def test_unauthorized_access(client: TestClient):
    branch_data = {"name": "ВДВ"}

    response = client.post("/branches/", json=branch_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_troop(client: TestClient, create_branch, user_with_token):
    troop_data = {"name": "Танковый батальон", "branch_id": create_branch["id"]}
    token = user_with_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/troops/", json=troop_data, headers=headers)
    assert response.status_code == 201
    assert "id" in response.json()

# Тестирование получения всех войск
@pytest.mark.asyncio
async def test_get_troops(client: TestClient, create_branch, user_with_token):
    response = client.get("/troops/")
    assert response.status_code == 200


# Тестирование получения войск по ID
@pytest.mark.asyncio
async def test_get_troop_by_id(client: TestClient, create_branch, user_with_token):
    troop_data = {"name": "Танковый батальон", "branch_id": create_branch["id"]}
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    response = client.post("/troops/", json=troop_data, headers=headers)
    troop_id = response.json()["id"]

    response = client.get(f"/troops/{troop_id}", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_troop_name(client: TestClient, create_branch, user_with_token):
    troop_data = {"name": "Танковый батальон", "branch_id": create_branch["id"]}
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    response = client.post("/troops/", json=troop_data, headers=headers)
    troop_id = response.json()["id"]

    updated_data = {"name": "Механизированный батальон", "branch_id": create_branch["id"]}
    response = client.patch(f"/troops/{troop_id}", json=updated_data, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_recruitment_office(client: TestClient, user_with_token):
    data = {
        "address": "Ульяновск, ул. Винновская роща, д.1",
        "chief_name": "Соколов Владимир Никиолаевич",
    }

    headers = {"Authorization": f"Bearer {user_with_token['token']}"}
    response = client.post("/recruitment_offices/", json=data, headers=headers)

    assert response.status_code == 201
    assert response.json()["address"] == data["address"]
    assert response.json()["chief_name"] == data["chief_name"]

# Неавторизованный
@pytest.mark.asyncio
async def test_create_recruitment_office_no_auth(client: TestClient, user_with_token):
    data = {
        "address": "Ульяновск, ул. Винновская роща, д.1",
        "chief_name": "Соколов Владимир Никиолаевич",
    }

    response = client.post("/recruitment_offices/", json=data)

    assert response.status_code == 401

@pytest_asyncio.fixture(scope="function")
async def create_recruitment_office(client: TestClient, user_with_token):
    office_data = {
        "address": "Ульяновск, ул. Винновская роща, д.1",
        "chief_name": "Соколов Владимир Никиолаевич",
    }
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    response = client.post("/recruitment_offices/", json=office_data, headers=headers)
    assert response.status_code == 201

    return response.json()

@pytest.mark.asyncio
async def test_get_recruitments(client: TestClient, user_with_token):
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    response = client.get("/recruitments/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_recruitment(client: TestClient, user_with_token, create_recruitment_office):
    recruitment_data = {
        "name": "Иванов И.В.",
        "address": "ул. Крымова",
        "date_of_birth": "2003-04-25",
        "marital_status": True,
        "recruitment_office_id": create_recruitment_office["id"],
    }
    updated_data = {
        "name": "Иванова И.В.",
        "address": "ул. Ленина",
        "date_of_birth": "2003-05-10",
        "marital_status": False,
        "recruitment_office_id": create_recruitment_office["id"],
    }

    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    # Сначала создаем призывника
    response = client.post("/recruitments/", json=recruitment_data, headers=headers)
    recruitment_id = response.json()["id"]

    # Теперь обновляем данные
    response = client.patch(f"/recruitments/{recruitment_id}", json=updated_data, headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_recruitment_noauth(client: TestClient, user_with_token, create_recruitment_office):
    recruitment_data = {
        "name": "Иванов И.В.",
        "address": "ул. Крымова",
        "date_of_birth": "2003-04-25",
        "marital_status": True,
        "recruitment_office_id": create_recruitment_office["id"],
    }
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    # Сначала создаем призывника
    response = client.post("/recruitments/", json=recruitment_data, headers=headers)
    recruitment_id = response.json()["id"]

    # Теперь удаляем его
    response = client.delete(f"/recruitments/{recruitment_id}")
    assert response.status_code == 401


# призывники
@pytest.mark.asyncio
async def test_create_recruitment(client: TestClient, user_with_token, create_recruitment_office):
    recruitment_data = {
        "name": "Иванов И.В.",
        "address": "ул. Крымова",
        "date_of_birth": "2003-04-25",
        "marital_status": True,
        "recruitment_office_id": create_recruitment_office["id"],  # ID из фикстуры
    }
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    response = client.post("/recruitments/", json=recruitment_data, headers=headers)
    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_delete_troop(client: TestClient, create_branch, user_with_token):
    troop_data = {"name": "Танковый батальон", "branch_id": create_branch["id"]}
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    # Создаем войска
    response = client.post("/troops/", json=troop_data, headers=headers)
    troop_id = response.json()["id"]

    response = client.delete(f"/troops/{troop_id}", headers=headers)
    assert response.status_code == 204

    # Проверяка
    response = client.get(f"/troops/{troop_id}", headers=headers)
    assert response.status_code == 404

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

@pytest.mark.asyncio
async def test_delete_recruitment(client: TestClient, user_with_token, create_recruitment_office):
    recruitment_data = {
        "name": "Иванов И.В.",
        "address": "ул. Крымова",
        "date_of_birth": "2003-04-25",
        "marital_status": True,
        "recruitment_office_id": create_recruitment_office["id"],
    }
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    # Сначала создаем призывника
    response = client.post("/recruitments/", json=recruitment_data, headers=headers)
    recruitment_id = response.json()["id"]

    # Теперь удаляем его
    response = client.delete(f"/recruitments/{recruitment_id}", headers=headers)
    assert response.status_code == 204


@pytest_asyncio.fixture(scope="function")
async def create_recruitment(client: TestClient, user_with_token, create_recruitment_office):
    recruitment_data = {
        "name": "Иванов Иван Иванович",
        "date_of_birth": "2000-05-15",
        "address": "г. Москва, ул. Пушкина, д. 10",
        "marital_status": True,
        "recruitment_office_id": create_recruitment_office["id"]
    }

    # Получаем токен из фикстуры user_with_token
    token = user_with_token["token"]
    headers = {"Authorization": f"Bearer {token}"}


    response = client.post("/recruitments/", json=recruitment_data, headers=headers)

    assert response.status_code == 201

    #print(response.json()["id"])
    return response.json()

@pytest.mark.asyncio
async def test_create_medexam(client: TestClient, user_with_token, create_recruitment):
    medexam_data = {
        "recruitment_id": create_recruitment["id"],
        "date_of_exam": "2025-02-20",
        "result": "не годен",
    }
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    response = client.post("/medexams/", json=medexam_data, headers=headers)
    # print(response)

    assert response.status_code == 201

@pytest.mark.asyncio
async def test_get_medexams(client: TestClient, user_with_token):
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    response = client.get("/medexams/", headers=headers)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_medexam_by_id(client: TestClient, user_with_token, create_recruitment):
    # Создаем медкомиссию
    medexam_data = {
        "recruitment_id": create_recruitment["id"],
        "date_of_exam": "2025-02-20",
        "result": "не годен",
    }
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}
    create_response = client.post("/medexams/", json=medexam_data, headers=headers)
    created_medexam = create_response.json()

    response = client.get(f"/medexams/{created_medexam['id']}", headers=headers)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_add_mode_work(client: TestClient, user_with_token, create_recruitment_office):
    mode_work_data = {
        "day": "Пн",  # День недели
        "work_start": "09:00:00",  # Время начала работы
        "work_end": "18:00:00",  # Время окончания работы
    }
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    response = client.post(f"/work_hours_office/{create_recruitment_office['id']}", json=mode_work_data, headers=headers)

    assert response.status_code == 201

    created_mode_work = response.json()
    assert created_mode_work["day"] == mode_work_data["day"]
    assert created_mode_work["work_start"] == mode_work_data["work_start"]
    assert created_mode_work["work_end"] == mode_work_data["work_end"]

@pytest.mark.asyncio
async def test_get_all_modes_work(client: TestClient, user_with_token, create_recruitment_office):
    mode_work_data_1 = {
        "day": "Пн",
        "work_start": "09:00:00",
        "work_end": "18:00:00",
    }
    mode_work_data_2 = {
        "day": "Вт",
        "work_start": "09:00:00",
        "work_end": "17:00:00",
    }
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}

    client.post(f"/work_hours_office/{create_recruitment_office['id']}", json=mode_work_data_1, headers=headers)
    client.post(f"/work_hours_office/{create_recruitment_office['id']}", json=mode_work_data_2, headers=headers)

    params = {"day": "Пн", "skip": 0, "limit": 2}

    response = client.get("/work_hours_office/", headers=headers, params=params)

    assert response.status_code == 200

    # не пуст и соответствует фильтрации
    modes_work = response.json()
    assert isinstance(modes_work, list)
    assert len(modes_work) > 0
    assert modes_work[0]["day"] == "Пн"  # <--

@pytest.mark.asyncio
async def test_delete_mode_work(client: TestClient, user_with_token, create_recruitment_office):
    mode_work_data = {
        "day": "Пн",
        "work_start": "09:00:00",
        "work_end": "18:00:00",
    }
    headers = {"Authorization": f"Bearer {user_with_token['token']}"}
    create_response = client.post(f"/work_hours_office/{create_recruitment_office['id']}", json=mode_work_data, headers=headers)
    created_mode_work = create_response.json()

    response = client.delete(f"/work_hours_office/{created_mode_work['id']}", headers=headers)

    assert response.status_code == 204
