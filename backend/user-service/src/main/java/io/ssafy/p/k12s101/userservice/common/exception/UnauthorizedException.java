package io.ssafy.p.k12s101.userservice.common.exception;

public class UnauthorizedException extends BaseException{

    public UnauthorizedException() {
        super(ErrorCode.UNAUTHORIZED);
    }
}
