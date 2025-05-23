package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.LoginUserCommand;
import io.ssafy.p.k12s101.userservice.service.dto.LoginUserResult;

@FunctionalInterface
public interface LoginUserService {

    // 로그인을 수행합니다.
    LoginUserResult handle(LoginUserCommand command);
}
