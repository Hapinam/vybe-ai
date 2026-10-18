"""Linear replay snapshots preserve all existing replay semantics."""
from dataclasses import asdict
from fastapi.testclient import TestClient
from vybe.engine import replay, replay_timeline
from vybe.main import app
from vybe.models import MatchDefinition

MATCH = {"match_id":"unsorted","home_team":"A","away_team":"B","events":[
 {"id":"g2","minute":60,"type":"goal","team":"B"},
 {"id":"k","minute":0,"type":"kickoff"},
 {"id":"g1","minute":20,"type":"goal","team":"A"},
 {"id":"p","minute":30,"type":"pass_completed","team":"A"}]}

def test_snapshots_match_partial_replay_including_zero():
    match=MatchDefinition.model_validate(MATCH)
    states=replay_timeline(match)
    assert len(states)==len(match.events)+1
    for i,state in enumerate(states):
        assert asdict(state)==asdict(replay(match,i))
    states[0].home_score=99
    assert states[1].home_score!=99

def test_existing_bulk_endpoint_preserves_contract():
    match=MatchDefinition.model_validate(MATCH)
    response=TestClient(app).post("/v1/matches/replay/states",json=MATCH)
    assert response.status_code==200
    assert response.json()["states"]==[asdict(s) for s in replay_timeline(match)[1:]]

def test_500_events_and_body_guard():
    match={**MATCH,"events":[{"id":f"e{i}","minute":i%120,"type":"pass_completed","team":"A"} for i in range(500)]}
    with TestClient(app) as client:
        response=client.post("/v1/matches/replay/states",json=match)
        assert response.status_code==200
        assert len(response.json()["states"])==500
        assert response.json()["states"][-1]["passes_home"]==500
        assert client.post("/v1/matches/replay/states",content=b" "*300000,headers={"content-type":"application/json"}).status_code==413
