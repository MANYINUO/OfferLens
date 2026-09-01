package com.offerlens;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * OfferLens 后端启动类。
 */
@SpringBootApplication
@MapperScan("com.offerlens.mapper")
@EnableScheduling
public class OfferLensApplication {

    public static void main(String[] args) {
        SpringApplication.run(OfferLensApplication.class, args);
    }
}
