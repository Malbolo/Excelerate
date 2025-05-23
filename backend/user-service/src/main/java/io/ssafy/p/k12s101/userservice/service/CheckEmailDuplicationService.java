package io.ssafy.p.k12s101.userservice.service;

@FunctionalInterface
public interface CheckEmailDuplicationService {

    // 사용자 이메일 중복 검사를 수행합니다.
    boolean handle(String email);
}
