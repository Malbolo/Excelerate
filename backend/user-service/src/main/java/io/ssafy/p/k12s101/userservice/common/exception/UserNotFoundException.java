package io.ssafy.p.k12s101.userservice.common.exception;

public class UserNotFoundException extends BaseException {

    public UserNotFoundException() {
        super(ErrorCode.USER_NOT_FOUND);
    }
}
