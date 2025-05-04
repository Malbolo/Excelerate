package io.ssafy.p.k12s101.userservice.controller.dto;

public record UpdateUserProfileRequest(
    String name,
    String department
) {
}
