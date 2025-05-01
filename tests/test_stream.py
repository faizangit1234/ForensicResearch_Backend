def test_generate_sequence_stream_success(client):
    res = client.get("/generate-sequence-stream/id_0001")
    assert res.status_code == 200
    text = res.text
    assert len(text) > 0  # got some sequence

def test_generate_sequence_stream_not_found(client):
    res = client.get("/generate-sequence-stream/999")
    assert res.status_code == 404
