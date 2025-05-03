package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.ChangeUserPasswordCommand;

@FunctionalInterface
public interface ChangeUserPasswordService {

    void handle(ChangeUserPasswordCommand command);
}
