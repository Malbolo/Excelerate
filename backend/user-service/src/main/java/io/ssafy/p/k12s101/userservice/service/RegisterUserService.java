package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.RegisterUserCommand;

@FunctionalInterface
public interface RegisterUserService {

    // 회원가입을 수행합니다.
    void handle(RegisterUserCommand command);
}
