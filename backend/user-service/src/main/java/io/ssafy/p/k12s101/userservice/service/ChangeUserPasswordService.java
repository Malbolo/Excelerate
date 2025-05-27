package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.ChangeUserPasswordCommand;

@FunctionalInterface
public interface ChangeUserPasswordService {

    // 사용자 비밀번호 변경 로직을 수행합니다.
    void handle(ChangeUserPasswordCommand command);
}
