package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.UpdateUserProfileCommand;

@FunctionalInterface
public interface UpdateUserProfileService {

    void handle(UpdateUserProfileCommand command);
}
