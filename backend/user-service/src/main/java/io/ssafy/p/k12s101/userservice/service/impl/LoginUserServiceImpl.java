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

    @Override
    @Transactional(readOnly = true)
    public LoginUserResult handle(LoginUserCommand command) {
        User user = userRepository.findByEmail(command.email())
            .orElseThrow(InvalidUserCredentialsException::new);

        if (!passwordEncoder.matches(command.password(), user.getPassword())) {
            throw new InvalidUserCredentialsException();
        }

        String token = jwtProvider.generateToken(user.getId());
        return new LoginUserResult(token);
    }
}
