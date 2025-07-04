package io.ssafy.p.k12s101.userservice.service.impl;

import io.ssafy.p.k12s101.userservice.common.exception.InvalidPasswordException;
import io.ssafy.p.k12s101.userservice.domain.User;
import io.ssafy.p.k12s101.userservice.domain.UserRepository;
import io.ssafy.p.k12s101.userservice.service.ChangeUserPasswordService;
import io.ssafy.p.k12s101.userservice.service.dto.ChangeUserPasswordCommand;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ChangeUserPasswordServiceImpl implements ChangeUserPasswordService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    // 사용자 비밀번호 변경 로직을 수행합니다.
    @Override
    @Transactional
    public void handle(ChangeUserPasswordCommand command) {
        User user = userRepository.findByIdOrElseThrow(command.userId());

        // 변경 전/후 비밀번호가 동일하다면 에러 발생.
        if (!passwordEncoder.matches(command.currentPassword(), user.getPassword())) {
            throw new InvalidPasswordException();
        }
        user.changePassword(passwordEncoder.encode(command.newPassword()));
    }
}
