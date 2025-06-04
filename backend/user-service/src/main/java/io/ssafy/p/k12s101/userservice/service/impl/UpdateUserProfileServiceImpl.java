package io.ssafy.p.k12s101.userservice.service.impl;

import io.ssafy.p.k12s101.userservice.domain.User;
import io.ssafy.p.k12s101.userservice.domain.UserRepository;
import io.ssafy.p.k12s101.userservice.service.UpdateUserProfileService;
import io.ssafy.p.k12s101.userservice.service.dto.UpdateUserProfileCommand;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UpdateUserProfileServiceImpl implements UpdateUserProfileService {

    private final UserRepository userRepository;

    /**
     * 사용자 정보 수정을 수행합니다.
     */
    @Override
    @Transactional
    public void handle(UpdateUserProfileCommand command) {
        User user = userRepository.findByIdOrElseThrow(command.userId());
        user.updateProfile(command.name(), command.department());
    }
}
