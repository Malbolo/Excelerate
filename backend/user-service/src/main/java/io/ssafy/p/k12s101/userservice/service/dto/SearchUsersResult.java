package io.ssafy.p.k12s101.userservice.service.dto;

import java.util.List;

public record SearchUsersResult(
    List<UserSummaryResult> users,
    int page,
    int size,
    long total
) {}
