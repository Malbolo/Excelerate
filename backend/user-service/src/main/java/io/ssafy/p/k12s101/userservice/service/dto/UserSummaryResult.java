package io.ssafy.p.k12s101.userservice.service.dto;

import io.ssafy.p.k12s101.userservice.domain.User;

public record UserSummaryResult(
    String uid,
    String name,
    String email,
    String department
) {

    public static UserSummaryResult of(User user) {
        return new UserSummaryResult(
            user.getId().toString(),
            user.getName(),
            user.getEmail(),
            user.getDepartment()
        );
    }
}
