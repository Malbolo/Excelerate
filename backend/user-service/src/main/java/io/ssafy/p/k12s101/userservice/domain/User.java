package io.ssafy.p.k12s101.userservice.domain;

import jakarta.persistence.*;
import lombok.*;

@Getter
@Entity
@Table(name = "users")
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 100)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false, length = 50)
    private String name;

    @Column(nullable = false, length = 100)
    private String department;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private UserRole role;

    @Builder
    public User(String email, String password, String name, String department, UserRole role) {
        this.email = email;
        this.password = password;
        this.name = name;
        this.department = department;
        this.role = role;
    }

    public void updateProfile(String name, String department) {
        this.name = name;
        this.department = department;
    }

    public void changePassword(String hashedPassword) {
        this.password = hashedPassword;
    }
}
