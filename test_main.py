from fastapi.testclient import TestClient

from main import app

client=TestClient(app)

#test home api
def test_home_api():
    response=client.get("/")
    assert response.status_code==200
    assert response.json()=={"message":"cors enable api"}

#test add api
def test_add_api():
    response=client.get("/add?a=2&b=3")
    assert response.status_code==200
    assert response.json()=={"result":5}
