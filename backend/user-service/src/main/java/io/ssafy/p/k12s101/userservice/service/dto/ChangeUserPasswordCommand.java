package io.ssafy.p.k12s101.userservice.service.dto;

public record ChangeUserPasswordCommand(
    Long userId,
    String currentPassword,
    String newPassword
) {
}
