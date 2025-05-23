package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.FindUserProfileResult;

@FunctionalInterface
public interface FindUserProfileService {

    // 사용자 정보를 조회합니다.
    FindUserProfileResult handle(Long userId);
}
