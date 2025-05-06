package io.ssafy.p.k12s101.userservice.common.interceptor;

import io.ssafy.p.k12s101.userservice.common.exception.UnauthenticatedException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

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

        if (isWhitelisted(path, request.getMethod())) {
            return true;
        }

        String userId = request.getHeader(USER_ID_HEADER);
        if (userId == null || userId.isBlank()) {
            throw new UnauthenticatedException();
        }

        return true;
    }

    private boolean isWhitelisted(String path, String method) {
        return switch (path) {
            case "/api/users" -> "POST".equalsIgnoreCase(method);
            case "/api/users/login", "/api/users/check-email" -> true;
            default -> false;
        };
    }
}
