package com.offerlens.controller;

import com.offerlens.common.Result;
import com.offerlens.job.ApplicationTimeoutJob;
import com.offerlens.service.StatsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 统计与定时任务接口
 */
@RestController
@RequestMapping("/api/stats")
public class StatsController {

    @Autowired
    private StatsService statsService;

    @Autowired
    private ApplicationTimeoutJob timeoutJob;

    /** 获取投递漏斗统计 */
    @GetMapping("/funnel")
    public Result<Map<String, Object>> getFunnel(@RequestParam Long userId) {
        return Result.success(statsService.getFunnelStats(userId));
    }

    /** 手动触发超时流转（方便测试） */
    @PostMapping("/timeout/run")
    public Result<Integer> runTimeoutJob() {
        int count = timeoutJob.runManually();
        return Result.success(count);
    }
}
