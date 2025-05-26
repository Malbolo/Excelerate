package io.ssafy.p.k12s101.userservice.service.impl;

import io.ssafy.p.k12s101.userservice.domain.UserRepository;
import io.ssafy.p.k12s101.userservice.service.CheckEmailDuplicationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CheckEmailDuplicationServiceImpl implements CheckEmailDuplicationService {

    private final UserRepository userRepository;

    /**
     * 동일한 이메일의 회원이 있다면 false를 반환합니다.
     * 없다면 true를 반환합니다.
     */
    @Override
    @Transactional(readOnly = true)
    public boolean handle(String email) {
        boolean exists = userRepository.existsByEmail(email);
        return !exists;
    }
}
