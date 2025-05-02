Agent 구조

그래프 모양
![graph](./outputv2.png)

입력 받은 command_list를 split 한뒤 각 list에 대해 code 생성

생성된 코드 실행 후 성공하면 완료. 실패 시 3번까지 재생성. 최종 실패 시 error 메시지를 남기고 종료

상태 구조
```
class AgentState(MessagesState):
    command_list: List[str]
    python_code: str
    dataframe: List[pd.DataFrame]
    retry_count: int
    error_msg: dict | None
    logs: List[dict]
```