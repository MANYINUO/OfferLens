package com.offerlens.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.offerlens.entity.Application;
import com.offerlens.mapper.ApplicationMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 投递漏斗统计服务
 * 统计各阶段投递数量、相邻阶段转化率
 */
@Service
public class StatsService {

    @Autowired
    private ApplicationMapper applicationMapper;

    /** 漏斗阶段顺序 */
    private static final List<String> FUNNEL_STAGES = List.of(
            "applied", "viewed", "written", "first", "second", "hr", "offer"
    );

    /**
     * 获取用户的投递漏斗统计
     * 返回：各阶段数量 + 相邻阶段转化率 + 终态数量
     */
    public Map<String, Object> getFunnelStats(Long userId) {
        Map<String, Object> result = new LinkedHashMap<>();

        // 1. 统计各阶段数量
        Map<String, Long> stageCounts = new LinkedHashMap<>();
        long total = 0;
        for (String stage : FUNNEL_STAGES) {
            LambdaQueryWrapper<Application> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(Application::getUserId, userId)
                   .eq(Application::getStatus, stage);
            long count = applicationMapper.selectCount(wrapper);
            stageCounts.put(stage, count);
            total += count;
        }
        result.put("stages", stageCounts);
        result.put("totalInFunnel", total);

        // 2. 统计终态数量
        Map<String, Long> terminalCounts = new LinkedHashMap<>();
        for (String terminal : List.of("rejected", "no_response", "abandoned")) {
            LambdaQueryWrapper<Application> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(Application::getUserId, userId)
                   .eq(Application::getStatus, terminal);
            terminalCounts.put(terminal, applicationMapper.selectCount(wrapper));
        }
        result.put("terminal", terminalCounts);

        // 3. 计算相邻阶段转化率（viewed/applied, written/viewed, ...）
        Map<String, Double> conversionRates = new LinkedHashMap<>();
        for (int i = 1; i < FUNNEL_STAGES.size(); i++) {
            String from = FUNNEL_STAGES.get(i - 1);
            String to = FUNNEL_STAGES.get(i);
            long fromCount = stageCounts.get(from);
            long toCount = stageCounts.get(to);
            // 转化率 = 到达下一阶段的数量 / 当前阶段数量（包含已经流过去的，所以用累计口径）
            // 简化版：toCount / fromCount，fromCount 为 0 时记为 0
            double rate = fromCount == 0 ? 0.0 : (double) toCount / fromCount * 100;
            conversionRates.put(from + "_to_" + to, Math.round(rate * 100.0) / 100.0);
        }
        result.put("conversionRates", conversionRates);

        // 4. 整体转化率（offer / applied）
        long appliedCount = stageCounts.get("applied");
        long offerCount = stageCounts.get("offer");
        double overallRate = appliedCount == 0 ? 0.0 : (double) offerCount / appliedCount * 100;
        result.put("overallRate", Math.round(overallRate * 100.0) / 100.0);

        return result;
    }
}
