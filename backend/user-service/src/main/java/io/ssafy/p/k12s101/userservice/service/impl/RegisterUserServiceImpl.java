package io.ssafy.p.k12s101.userservice.service.impl;

import io.ssafy.p.k12s101.userservice.common.exception.EmailAlreadyUsedException;
import io.ssafy.p.k12s101.userservice.domain.User;
import io.ssafy.p.k12s101.userservice.domain.UserRepository;
import io.ssafy.p.k12s101.userservice.domain.UserRole;
import io.ssafy.p.k12s101.userservice.service.RegisterUserService;
import io.ssafy.p.k12s101.userservice.service.dto.RegisterUserCommand;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class RegisterUserServiceImpl implements RegisterUserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    /**
     * 사용자 회원가입을 수행합니다.
     */
    @Override
    @Transactional
    public void handle(RegisterUserCommand command) {
        if (userRepository.existsByEmail(command.email())) {
            throw new EmailAlreadyUsedException();
        }

        User user = User.builder()
            .email(command.email())
            .password(passwordEncoder.encode(command.password()))
            .name(command.name())
            .department(command.department())
            .role(UserRole.USER)
            .build();

        userRepository.save(user);
    }
}
