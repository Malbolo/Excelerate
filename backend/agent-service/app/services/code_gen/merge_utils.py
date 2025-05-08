import re
from typing import List

_fence_pat = re.compile(r"```(?:python)?\n([\s\S]*?)```", re.IGNORECASE)
_def_pat   = re.compile(r"^def\s+\w+\s*\(.*\)\s*:")

def merge_code_snippets(snippets: List[str]) -> str:
    """
    여러 스니펫을 하나의 실행 가능한 스크립트로 병합.
    - import 구문을 맨 위로 모아 중복 제거
    - 첫 스니펫에서만 intermediate 초기화
    - 함수 래퍼 제거 후, 본문만 삽입
    - 마지막에 intermediate 표현식은 한 번만 남김
    """
    imports: List[str] = []
    seen_imports = set()
    bodies: List[List[str]] = []

    for idx, text in enumerate(snippets):
        # 1) fenced code block에서 실제 코드만 추출
        m = _fence_pat.search(text)
        code = m.group(1) if m else text
        lines = code.splitlines()

        # 2) import 들만 따로 모으고, 나머지는 body에 보관
        body: List[str] = []
        for ln in lines:
            if ln.startswith("import ") or ln.startswith("from "):
                if ln not in seen_imports:
                    imports.append(ln)
                    seen_imports.add(ln)
            else:
                body.append(ln)

        # 3) 첫 스니펫 이후엔 intermediate 초기화 라인 제거
        if idx > 0 and body and body[0].strip().startswith("intermediate") and "=" in body[0]:
            body = body[1:]

        # 4) 함수 래퍼(def …) 제거 및 indent 풀기
        if body and _def_pat.match(body[0]):
            inner: List[str] = []
            for ln in body[1:]:
                inner.append(ln[4:] if ln.startswith("    ") else ln)
            body = inner

        bodies.append(body)

    # 5) 중복된 intermediate 표현식 제거 (마지막 블록만 남김)
    for i in range(len(bodies) - 1):
        if bodies[i] and bodies[i][-1].strip() == "intermediate":
            bodies[i].pop()

    # 6) 최종 조합: imports → 빈줄 → 각 body
    out_lines: List[str] = []
    out_lines.extend(imports)
    if imports:
        out_lines.append("")

    for block in bodies:
        out_lines.extend(block)
        out_lines.append("")

    # 7) 마지막 불필요한 빈줄 제거
    if out_lines and out_lines[-1] == "":
        out_lines.pop()

    return "\n".join(out_lines)
