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

    @Override
    @Transactional(readOnly = true)
    public boolean handle(String email) {
        boolean exists = userRepository.existsByEmail(email);
        return !exists;
    }
}
