package io.ssafy.p.k12s101.userservice.common.util;

import io.jsonwebtoken.Jwts;
import io.ssafy.p.k12s101.userservice.common.config.JwtProperties;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
import java.util.Date;

@Component
public class JwtProvider {

    private final SecretKey secretKey;
    private final JwtProperties jwtProperties;

    @Autowired
    public JwtProvider(JwtProperties jwtProperties) {
        this.jwtProperties = jwtProperties;
        this.secretKey = new SecretKeySpec(Base64.getDecoder().decode(jwtProperties.secret()), "HmacSHA256");
    }

    public String generateToken(Long userId) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + jwtProperties.expirationSeconds() * 1000);

        return Jwts.builder()
            .subject(userId.toString())
            .issuedAt(now)
            .expiration(expiry)
            .signWith(secretKey)
            .compact();
    }
}
