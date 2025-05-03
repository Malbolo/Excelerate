package io.ssafy.p.k12s101.userservice.controller.dto;

public record ErrorResponse(
    String result,
    String code,
    String message
) {
    public static ErrorResponse of(String code, String message) {
        return new ErrorResponse("error", code, message);
    }
}
