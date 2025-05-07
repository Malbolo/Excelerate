import redis
import os
import json
from datetime import timedelta
from app.models.log import LogDetail
from uuid import uuid4
import pandas as pd

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB   = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def generate_log_id(user_id: str) -> str:
    # timestamp = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")
    return f"logs:{user_id}:{uuid4().hex}"

def save_logs_to_redis(log_id: str, logs: list[LogDetail], ttl_minutes: int = 60*24*7): # 1주 보관
    logs_json = json.dumps([log.model_dump(mode="json") for log in logs])
    redis_client.setex(log_id, timedelta(minutes=ttl_minutes), logs_json)

def get_logs_from_redis(log_id: str) -> list[dict] | None:
    data = redis_client.get(log_id)
    if data:
        return json.loads(data)
    return None

def serialize_state(state: dict) -> dict:
    """
    AgentState에서 Redis에 저장할 최소 상태만 뽑아서
    JSON-serializable 형태로 변환합니다.
    """
    # 1) DataFrame 리스트 직렬화 (Timestamp → ISO 문자열)
    serialized_frames = []
    for df in state["dataframe"]:
        # 날짜 컬럼을 ISO 포맷 문자열로 변환
        df_copy = df.copy()
        for col in df_copy.select_dtypes(include=['datetime64[ns]', 'datetimetz']):
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%dT%H:%M:%S')
        serialized_frames.append(df_copy.to_dict(orient="records"))

    return {
        "queue_idx":          state["queue_idx"],
        "classified_cmds":    state["classified_cmds"],
        "python_codes_list":  state["python_codes_list"],
        "dataframe":          serialized_frames,
        "logs": [
            log.model_dump(mode="json")
            for log in state["logs"]
        ],
    }

def save_states_to_redis(session_id: str, state: dict, ttl_minutes: int = 30): # 세션은 30분만 보관
    """
    세션 상태(state)를 Redis에 저장합니다.
    :param session_id: 저장할 Redis 키 (예: "sessions:{user_id}:{uid}")
    :param state: JSON 직렬화 가능한 state 딕셔너리
    :param ttl_minutes: 만료 시간(분) 기본값 1일(1440분)
    """
    s_state = serialize_state(state)
    state_json = json.dumps(s_state)
    redis_client.setex(session_id, timedelta(minutes=ttl_minutes), state_json)


def get_states_from_redis(session_id: str) -> dict | None:
    """
    Redis에서 세션 상태(state)를 조회하고, rehydrate하여 AgentState 형태로 반환합니다.
    :param session_id: 조회할 Redis 키
    :return: 재구성된 상태 딕셔너리 또는 None
    """
    data = redis_client.get(session_id)
    if not data:
        return None

    raw = json.loads(data)
    # DataFrame 리스트 복원
    df_list = [pd.DataFrame(records) for records in raw.get("dataframe", [])]
    # LogDetail 리스트 복원
    log_list = [LogDetail(**ld) for ld in raw.get("logs", [])]

    # 최소 상태만 재구성
    state = {
        "queue_idx":          raw.get("queue_idx", 0),
        "classified_cmds":    raw.get("classified_cmds", []),
        "python_codes_list":  raw.get("python_codes_list", []),
        "dataframe":          df_list,
        "logs":               log_list,
    }
    return state

