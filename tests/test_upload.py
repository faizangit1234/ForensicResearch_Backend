import io


def test_upload_csv_success(client):
    data = {"file": ("test.csv", "id,region,age,seed\n3,emea,40,aagt", "text/csv")}
    response = client.post("/upload-csv/", files=data)
    assert response.status_code == 200
    body = response.json()
    assert "message" in body and "Processed 1 records" in body["message"]


def test_upload_csv_wrong_type(client):
    data = {"file": ("test.txt", "hello", "text/plain")}
    res = client.post("/upload-csv/", files=data)
    assert res.status_code == 400


def test_upload_csv_oversize(client, monkeypatch):
    # generate >5MB of "a"
    big = b"a" * (6 * 1024 * 1024)
    data = {"file": ("big.csv", big, "text/csv")}
    res = client.post("/upload-csv/", files=data)
    assert res.status_code == 413
