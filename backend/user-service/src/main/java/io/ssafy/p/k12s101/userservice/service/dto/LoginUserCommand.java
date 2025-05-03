package io.ssafy.p.k12s101.userservice.service.dto;

public record LoginUserCommand(
    String email,
    String password
) {
}
