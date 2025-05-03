package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.LoginUserCommand;
import io.ssafy.p.k12s101.userservice.service.dto.LoginUserResult;

@FunctionalInterface
public interface LoginUserService {

    LoginUserResult handle(LoginUserCommand command);
}
