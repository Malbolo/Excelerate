package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.RegisterUserCommand;

@FunctionalInterface
public interface RegisterUserService {

    void handle(RegisterUserCommand command);
}
