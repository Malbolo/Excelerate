package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.UpdateUserProfileCommand;

@FunctionalInterface
public interface UpdateUserProfileService {

    // 사용자 정보 수정을 수행합니다.
    void handle(UpdateUserProfileCommand command);
}
