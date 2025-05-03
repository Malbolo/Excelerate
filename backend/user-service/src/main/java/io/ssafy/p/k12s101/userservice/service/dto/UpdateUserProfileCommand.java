package io.ssafy.p.k12s101.userservice.service.dto;

public record UpdateUserProfileCommand(
    Long userId,
    String name,
    String department
) {
}
