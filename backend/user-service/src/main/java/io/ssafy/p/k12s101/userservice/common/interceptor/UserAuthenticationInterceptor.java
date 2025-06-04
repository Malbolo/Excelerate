package io.ssafy.p.k12s101.userservice.common.interceptor;

import io.ssafy.p.k12s101.userservice.common.exception.UnauthenticatedException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * 사용자의 인증 상태를 확인하는 인터셉터
 * - 인증이 필요한 요청에 대해 'X-User-Id' 헤더가 존재하는지 검사합니다.
 * - 존재하지 않으면 UnauthenticatedException 예외를 발생시킵니다.
 */
@Component
public class UserAuthenticationInterceptor implements HandlerInterceptor {

    private static final String USER_ID_HEADER = "X-User-Id";

    @Override
    public boolean preHandle(
        @NonNull HttpServletRequest request,
        @NonNull HttpServletResponse response,
        @NonNull Object handler
    ) {
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            return true;
        }

        String path = request.getRequestURI();

        // 인증이 필요하지 않은 경우는 통과합니다.
        if (isWhitelisted(path, request.getMethod())) {
            return true;
        }

        // 유효하지 않은 사용자 id인 경우 에러 발생.
        String userId = request.getHeader(USER_ID_HEADER);
        if (userId == null || userId.isBlank()) {
            throw new UnauthenticatedException();
        }

        return true;
    }

    /**
     * 인증이 필요하지 않은 요청 처리
     */
    private boolean isWhitelisted(String path, String method) {
        return switch (path) {
            case "/api/users" -> "POST".equalsIgnoreCase(method);
            case "/api/users/login", "/api/users/check-email" -> true;
            default -> false;
        };
    }
}
