package io.ssafy.p.k12s101.userservice.controller.dto;

public record SuccessResponse<T>(
    String result,
    T data
) {
    public static <T> SuccessResponse<T> success(T data) {
        return new SuccessResponse<>("success", data);
    }

    public static <T> SuccessResponse<T> success() {
        return new SuccessResponse<>("success", null);
    }
}
