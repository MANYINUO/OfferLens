package com.offerlens.job;

import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.offerlens.entity.Application;
import com.offerlens.mapper.ApplicationMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

/**
 * 投递超时自动流转定时任务
 *
 * 规则：投递后超过 14 天未推进（仍为 applied 状态），自动标记为 no_response
 * 每天凌晨 2 点执行一次
 */
@Component
public class ApplicationTimeoutJob {

    private static final Logger log = LoggerFactory.getLogger(ApplicationTimeoutJob.class);

    @Autowired
    private ApplicationMapper applicationMapper;

    /** 超过多少天未推进算无回音 */
    private static final int TIMEOUT_DAYS = 14;

    @Scheduled(cron = "0 0 2 * * ?")
    public void markNoResponse() {
        LocalDateTime threshold = LocalDateTime.now().minusDays(TIMEOUT_DAYS);

        LambdaUpdateWrapper<Application> wrapper = new LambdaUpdateWrapper<>();
        wrapper.eq(Application::getStatus, "applied")
               .lt(Application::getLastFollowupAt, threshold)
               .set(Application::getStatus, "no_response")
               .set(Application::getLastFollowupAt, LocalDateTime.now());

        int count = applicationMapper.update(null, wrapper);
        log.info("超时流转定时任务执行完成，共 {} 条投递标记为 no_response", count);
    }

    /**
     * 手动触发一次（方便测试，不依赖等到凌晨2点）
     */
    public int runManually() {
        LocalDateTime threshold = LocalDateTime.now().minusDays(TIMEOUT_DAYS);

        LambdaUpdateWrapper<Application> wrapper = new LambdaUpdateWrapper<>();
        wrapper.eq(Application::getStatus, "applied")
               .lt(Application::getLastFollowupAt, threshold)
               .set(Application::getStatus, "no_response")
               .set(Application::getLastFollowupAt, LocalDateTime.now());

        return applicationMapper.update(null, wrapper);
    }
}
