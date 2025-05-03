package io.ssafy.p.k12s101.userservice.common.exception;

public class EmailAlreadyUsedException extends BaseException {
    public EmailAlreadyUsedException() {
        super(ErrorCode.EMAIL_ALREADY_USED);
    }
}
