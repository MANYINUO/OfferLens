package com.offerlens;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * OfferLens 后端启动类。
 *
 * <p>@MapperScan 指向后续的 mapper 包，Step 1.2 起会有实际的 Mapper 接口。
 */
@SpringBootApplication
@MapperScan("com.offerlens.mapper")
public class OfferLensApplication {

    public static void main(String[] args) {
        SpringApplication.run(OfferLensApplication.class, args);
    }
}
