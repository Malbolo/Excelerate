package io.ssafy.p.k12s101.userservice.controller;

import io.ssafy.p.k12s101.userservice.controller.dto.ChangeUserPasswordRequest;
import io.ssafy.p.k12s101.userservice.controller.dto.CheckEmailDuplicationResponse;
import io.ssafy.p.k12s101.userservice.controller.dto.SuccessResponse;
import io.ssafy.p.k12s101.userservice.controller.dto.UpdateUserProfileRequest;
import io.ssafy.p.k12s101.userservice.service.*;
import io.ssafy.p.k12s101.userservice.service.dto.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final LoginUserService loginUserService;
    private final SearchUsersService searchUsersService;
    private final RegisterUserService registerUserService;
    private final FindUserProfileService findUserProfileService;
    private final UpdateUserProfileService updateUserProfileService;
    private final ChangeUserPasswordService changeUserPasswordService;
    private final CheckEmailDuplicationService checkEmailDuplicationService;

    // 사용자 회원가입
    @PostMapping
    public ResponseEntity<SuccessResponse<Void>> register(@RequestBody RegisterUserCommand command) {
        registerUserService.handle(command);
        return ResponseEntity.ok(SuccessResponse.success());
    }

    // 이메일 중복 검사
    @GetMapping("/check-email")
    public ResponseEntity<SuccessResponse<CheckEmailDuplicationResponse>> checkEmail(@RequestParam String email) {
        boolean available = checkEmailDuplicationService.handle(email);
        CheckEmailDuplicationResponse result = new CheckEmailDuplicationResponse(available);
        return ResponseEntity.ok(SuccessResponse.success(result));
    }

    // 로그인
    @PostMapping("/login")
    public ResponseEntity<SuccessResponse<LoginUserResult>> login(@RequestBody LoginUserCommand command) {
        LoginUserResult result = loginUserService.handle(command);
        return ResponseEntity.ok(SuccessResponse.success(result));
    }

    // 사용자 정보 조회
    @GetMapping("/me/profile")
    public ResponseEntity<SuccessResponse<FindUserProfileResult>> getProfile(@RequestHeader("X-User-Id") Long userId) {
        FindUserProfileResult result = findUserProfileService.handle(userId);
        return ResponseEntity.ok(SuccessResponse.success(result));
    }

    // 사용자 정보 수정
    @PatchMapping("/me/profile")
    public HttpEntity<SuccessResponse<Void>> updateProfile(
        @RequestHeader("X-User-Id") Long userId,
        @RequestBody UpdateUserProfileRequest body
    ) {
        UpdateUserProfileCommand command = new UpdateUserProfileCommand(
            userId,
            body.name(),
            body.department()
        );
        updateUserProfileService.handle(command);
        return ResponseEntity.ok(SuccessResponse.success());
    }

    // 사용자 비밀번호 변경
    @PatchMapping("/me/password")
    public ResponseEntity<SuccessResponse<Void>> changePassword(
        @RequestHeader("X-User-Id") Long userId,
        @RequestBody ChangeUserPasswordRequest body
    ) {
        ChangeUserPasswordCommand command = new ChangeUserPasswordCommand(
            userId,
            body.currentPassword(),
            body.newPassword()
        );
        changeUserPasswordService.handle(command);
        return ResponseEntity.ok(SuccessResponse.success());
    }

    // 사용자 목록 조회
    @GetMapping
    public ResponseEntity<?> searchUsers(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(required = false) String name
    ) {
        SearchUsersCommand command = new SearchUsersCommand(page, size, name);
        SearchUsersResult result = searchUsersService.handle(command);
        return ResponseEntity.ok(SuccessResponse.success(result));
    }
}
