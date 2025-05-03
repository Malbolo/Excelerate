package io.ssafy.p.k12s101.userservice.common.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;

@Getter
@RequiredArgsConstructor
public enum ErrorCode {

    INVALID_CREDENTIALS("U001", "Invalid credentials", 401),
    EMAIL_ALREADY_USED("U002", "Email is already in use", 409),
    USER_NOT_FOUND("U003", "User not found", 404),
    INVALID_PASSWORD("U004", "Current password is incorrect", 400);

    private final String code;
    private final String message;
    private final int statusCode;
}
