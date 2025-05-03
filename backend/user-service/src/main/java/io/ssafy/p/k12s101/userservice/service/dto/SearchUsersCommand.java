package io.ssafy.p.k12s101.userservice.service.dto;

public record SearchUsersCommand(
    int page,
    int size,
    String name
) {}
