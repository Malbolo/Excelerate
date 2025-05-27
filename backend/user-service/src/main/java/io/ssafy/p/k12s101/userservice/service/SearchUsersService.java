package io.ssafy.p.k12s101.userservice.service;

import io.ssafy.p.k12s101.userservice.service.dto.SearchUsersCommand;
import io.ssafy.p.k12s101.userservice.service.dto.SearchUsersResult;

@FunctionalInterface
public interface SearchUsersService {

    // 사용자를 조회합니다.
    SearchUsersResult handle(SearchUsersCommand command);
}
