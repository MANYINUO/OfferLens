package com.offerlens;

import org.junit.jupiter.api.Test;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * 验证 BCrypt 依赖（spring-security-crypto）确实可用。
 *
 * <p>V2 手册 Step 0.2 新增了这条依赖，但它的用途要到 Step 1.2 才体现。
 * 提前在骨架阶段验证一次，可以避免到写注册接口时才发现依赖缺失。
 * 同时这也锁定了 Step 1.2 验收里"密码是 $2a$ 开头的密文"这个约定。
 */
class PasswordEncoderTests {

    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    @Test
    void bcryptHashIsAvailableAndVerifiable() {
        String raw = "offerlens-secret";
        String hash = encoder.encode(raw);

        assertThat(hash).startsWith("$2a$");
        assertThat(hash).isNotEqualTo(raw);
        assertThat(encoder.matches(raw, hash)).isTrue();
        assertThat(encoder.matches("wrong-password", hash)).isFalse();
    }
}
