package io.ssafy.p.k12s101.userservice.service.dto;

public record FindUserProfileResult(
    String name,
    String email,
    String department
) {
}
