def test_generate_sequence_success(client):
    res = client.get("/generate-sequence/id_0994")
    assert res.status_code == 200
    data = res.json()
    assert data["sample_id"] == "id_0994"
    assert "dna_sequence" in data


def test_generate_sequence_not_found(client):
    res = client.get("/generate-sequence/999")
    assert res.status_code == 404

def test_compare_sequences_success(client):
    payload = {"id1": "id_0001", "id2": "id_0002"}

    res = client.post("/compare-sequences/", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "similarity_score" in body
    assert body["comparison_method"] == "hybrid_jaccard_nw"

def test_compare_sequences_missing(client):
    payload = {"id1": "1", "id2": "999"}
    res = client.post("/compare-sequences/", json=payload)
    assert res.status_code == 404
