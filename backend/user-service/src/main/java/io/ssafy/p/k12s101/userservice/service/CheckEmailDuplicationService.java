package io.ssafy.p.k12s101.userservice.service;

@FunctionalInterface
public interface CheckEmailDuplicationService {

    boolean handle(String email);
}
