package io.ssafy.p.k12s101.userservice.service.impl;

import io.ssafy.p.k12s101.userservice.domain.User;
import io.ssafy.p.k12s101.userservice.domain.UserRepository;
import io.ssafy.p.k12s101.userservice.service.FindUserProfileService;
import io.ssafy.p.k12s101.userservice.service.dto.FindUserProfileResult;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class FindUserProfileServiceImpl implements FindUserProfileService {

    private final UserRepository userRepository;

    /**
     * 사용자 정보를 조회합니다.
     * 이름, 이메일, 부서, 권한을 반환합니다.
     */
    @Override
    @Transactional(readOnly = true)
    public FindUserProfileResult handle(Long userId) {
        User user = userRepository.findByIdOrElseThrow(userId);

        return new FindUserProfileResult(
            user.getName(),
            user.getEmail(),
            user.getDepartment(),
            user.getRole().name()
        );
    }
}
