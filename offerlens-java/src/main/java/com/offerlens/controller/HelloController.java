package com.offerlens.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 骨架自检接口，用于验证服务能正常启动。
 *
 * <p>Step 1.1 之后所有接口都会改成返回统一的 Result 封装。
 */
@RestController
@RequestMapping("/api")
public class HelloController {

    @GetMapping("/hello")
    public String hello() {
        return "offerlens is running";
    }
}
