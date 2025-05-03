package io.ssafy.p.k12s101.userservice.common.exception;

public class InvalidUserCredentialsException extends BaseException {

    public InvalidUserCredentialsException() {
        super(ErrorCode.INVALID_CREDENTIALS);
    }
}
