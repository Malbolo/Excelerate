package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.FindUserProfileResult;

@FunctionalInterface
public interface FindUserProfileService {

    FindUserProfileResult handle(Long userId);
}
