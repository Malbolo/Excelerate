package io.ssafy.p.k12s101.userservice.common.interceptor;

import io.ssafy.p.k12s101.userservice.common.exception.UnauthorizedException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * 관리자 권한 확인용 인터셉터
 * - 모든 GET 요청에 대해 'X-User-Role' 헤더가 'ADMIN'인지 확인합니다.
 * - 그렇지 않으면 UnauthorizedException을 발생시켜 접근을 차단합니다.
 */
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
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            return true;
        }

        if (!"GET".equalsIgnoreCase(request.getMethod())) {
            return true;
        }

        // ADMIN으로 확인되지 않는 경우 에러 발생.
        String role = request.getHeader(ROLE_HEADER);
        if (role == null || !role.equals(ADMIN_ROLE)) {
            throw new UnauthorizedException();
        }
        return true;
    }
}
