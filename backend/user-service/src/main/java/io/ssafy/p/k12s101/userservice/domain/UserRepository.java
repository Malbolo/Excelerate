package io.ssafy.p.k12s101.userservice.domain;

import io.ssafy.p.k12s101.userservice.common.exception.UserNotFoundException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    default User findByIdOrElseThrow(Long id) {
        return findById(id).orElseThrow(UserNotFoundException::new);
    }

    boolean existsByEmail(String email);
    Optional<User> findByEmail(String email);
    Page<User> findByNameContaining(String name, Pageable pageable);
}
