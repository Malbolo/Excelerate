package io.ssafy.p.k12s101.userservice.common.interceptor;

import io.ssafy.p.k12s101.userservice.common.exception.UnauthorizedException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
@RequiredArgsConstructor
public class AdminAuthorizationInterceptor implements HandlerInterceptor {

    private static final String ROLE_HEADER = "X-User-Role";
    private static final String ADMIN_ROLE = "ADMIN";

    @Override
    public boolean preHandle(
        @NonNull HttpServletRequest request,
        @NonNull HttpServletResponse response,
        @NonNull Object handler
    ) {
        if (!"GET".equalsIgnoreCase(request.getMethod())) {
            return true;
        }

        String role = request.getHeader(ROLE_HEADER);
        if (role == null || !role.equals(ADMIN_ROLE)) {
            throw new UnauthorizedException();
        }
        return true;
    }
}
