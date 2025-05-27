package io.ssafy.p.k12s101.userservice.controller.dto;

public record ChangeUserPasswordRequest(
    String currentPassword,
    String newPassword
) {
}
