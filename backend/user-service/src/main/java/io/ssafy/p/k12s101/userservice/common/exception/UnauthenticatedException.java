package io.ssafy.p.k12s101.userservice.common.exception;

public class UnauthenticatedException extends BaseException {

    public UnauthenticatedException() {
        super(ErrorCode.UNAUTHENTICATED);
    }
}
