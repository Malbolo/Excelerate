package io.ssafy.p.k12s101.userservice.service.impl;

import io.ssafy.p.k12s101.userservice.common.exception.InvalidUserCredentialsException;
import io.ssafy.p.k12s101.userservice.common.util.JwtProvider;
import io.ssafy.p.k12s101.userservice.domain.User;
import io.ssafy.p.k12s101.userservice.domain.UserRepository;
import io.ssafy.p.k12s101.userservice.service.LoginUserService;
import io.ssafy.p.k12s101.userservice.service.dto.LoginUserCommand;
import io.ssafy.p.k12s101.userservice.service.dto.LoginUserResult;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class LoginUserServiceImpl implements LoginUserService {

    private final JwtProvider jwtProvider;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    /**
     * 로그인을 수행합니다.
     * 비밀번호가 올바르지 않다면 에러가 발생됩니다.
     * 사용자 정보를 JWT 토큰에 담아 반환합니다.
     */
    @Override
    @Transactional(readOnly = true)
    public LoginUserResult handle(LoginUserCommand command) {
        User user = userRepository.findByEmail(command.email())
            .orElseThrow(InvalidUserCredentialsException::new);

        if (!passwordEncoder.matches(command.password(), user.getPassword())) {
            throw new InvalidUserCredentialsException();
        }

        String token = jwtProvider.generateToken(user.getId(), user.getRole().name());
        return new LoginUserResult(token);
    }
}
