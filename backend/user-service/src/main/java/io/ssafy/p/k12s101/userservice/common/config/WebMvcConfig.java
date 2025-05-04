package io.ssafy.p.k12s101.userservice.common.config;

import io.ssafy.p.k12s101.userservice.common.interceptor.AdminAuthorizationInterceptor;
import io.ssafy.p.k12s101.userservice.common.interceptor.UserAuthenticationInterceptor;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@RequiredArgsConstructor
public class WebMvcConfig implements WebMvcConfigurer {

    private final UserAuthenticationInterceptor userAuthenticationInterceptor;
    private final AdminAuthorizationInterceptor adminAuthorizationInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(userAuthenticationInterceptor)
            .addPathPatterns("/api/users/me/**");

        registry.addInterceptor(adminAuthorizationInterceptor)
            .addPathPatterns("/api/users");
    }
}
