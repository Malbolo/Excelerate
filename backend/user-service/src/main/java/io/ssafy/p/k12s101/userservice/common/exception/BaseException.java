package io.ssafy.p.k12s101.userservice.common.exception;

import lombok.Getter;

@Getter
public abstract class BaseException extends RuntimeException {

    private final ErrorCode errorCode;

    protected BaseException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }

    public int getStatus() {
        return errorCode.getStatusCode();
    }

    public String getCode() {
        return errorCode.getCode();
    }

    @Override
    public String getMessage() {
        return errorCode.getMessage();
    }
}
