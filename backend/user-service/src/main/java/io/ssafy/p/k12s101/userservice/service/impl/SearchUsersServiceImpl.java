package io.ssafy.p.k12s101.userservice.service.impl;

import io.ssafy.p.k12s101.userservice.domain.User;
import io.ssafy.p.k12s101.userservice.domain.UserRepository;
import io.ssafy.p.k12s101.userservice.service.SearchUsersService;
import io.ssafy.p.k12s101.userservice.service.dto.SearchUsersCommand;
import io.ssafy.p.k12s101.userservice.service.dto.SearchUsersResult;
import io.ssafy.p.k12s101.userservice.service.dto.UserSummaryResult;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class SearchUsersServiceImpl implements SearchUsersService {

    private final UserRepository userRepository;

    /**
     * 사용자 목록을 조회 후, 페이지네이션을 수행합니다.
     */
    @Override
    @Transactional(readOnly = true)
    public SearchUsersResult handle(SearchUsersCommand command) {
        PageRequest pageRequest = PageRequest.of(command.page() - 1, command.size());

        Page<User> page = (command.name() == null || command.name().isBlank())
            ? userRepository.findAll(pageRequest)
            : userRepository.findByNameContaining(command.name(), pageRequest);

        List<UserSummaryResult> users = page.getContent().stream()
            .map(UserSummaryResult::of)
            .toList();

        return new SearchUsersResult(
            users,
            command.page(),
            command.size(),
            page.getTotalElements()
        );
    }
}
