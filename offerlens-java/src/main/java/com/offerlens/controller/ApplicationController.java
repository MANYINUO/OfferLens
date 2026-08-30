package com.offerlens.controller;

import com.offerlens.common.Result;
import com.offerlens.entity.Application;
import com.offerlens.service.ApplicationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 投递记录接口（含七阶段状态机）
 */
@RestController
@RequestMapping("/api/applications")
public class ApplicationController {

    @Autowired
    private ApplicationService applicationService;

    /** 创建投递记录（初始状态 applied） */
    @PostMapping
    public Result<Application> create(@RequestBody Map<String, Object> body) {
        Long userId = Long.valueOf(body.get("userId").toString());
        Long jdId = body.get("jdId") != null ? Long.valueOf(body.get("jdId").toString()) : null;
        Long resumeId = body.get("resumeId") != null ? Long.valueOf(body.get("resumeId").toString()) : null;
        String company = (String) body.get("company");
        String position = (String) body.get("position");
        String channel = (String) body.get("channel");
        String jobType = (String) body.get("jobType");
        Integer matchScore = body.get("matchScore") != null ? Integer.valueOf(body.get("matchScore").toString()) : null;
        String notes = (String) body.get("notes");
        return Result.success(applicationService.create(userId, jdId, resumeId,
                company, position, channel, jobType, matchScore, notes));
    }

    /** 查询用户的所有投递记录 */
    @GetMapping
    public Result<List<Application>> list(@RequestParam Long userId,
                                          @RequestParam(required = false) String status) {
        if (status != null && !status.isEmpty()) {
            return Result.success(applicationService.listByUserAndStatus(userId, status));
        }
        return Result.success(applicationService.listByUser(userId));
    }

    /** 查询单条投递记录 */
    @GetMapping("/{id}")
    public Result<Application> getById(@PathVariable Long id) {
        Application app = applicationService.getById(id);
        if (app == null) {
            return Result.error("投递记录不存在");
        }
        return Result.success(app);
    }

    /**
     * 推进状态（前进一步）
     * applied → viewed → written → first → second → hr → offer
     */
    @PostMapping("/{id}/advance")
    public Result<Application> advance(@PathVariable Long id) {
        Application app = applicationService.advance(id);
        if (app == null) {
            return Result.error("已到终态，无法继续推进");
        }
        return Result.success(app);
    }

    /**
     * 流转到指定状态（含终态）
     * 合法流转会校验，非法流转返回错误
     */
    @PostMapping("/{id}/transition")
    public Result<Application> transition(@PathVariable Long id, @RequestBody Map<String, String> body) {
        String targetStatus = body.get("status");
        try {
            Application app = applicationService.transition(id, targetStatus);
            if (app == null) {
                return Result.error("投递记录不存在");
            }
            return Result.success(app);
        } catch (IllegalArgumentException e) {
            return Result.error(e.getMessage());
        }
    }

    /** 更新备注 */
    @PutMapping("/{id}/notes")
    public Result<Void> updateNotes(@PathVariable Long id, @RequestBody Map<String, String> body) {
        String notes = body.get("notes");
        boolean ok = applicationService.updateNotes(id, notes);
        return ok ? Result.success() : Result.error("更新失败");
    }

    /** 删除投递记录 */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        boolean ok = applicationService.delete(id);
        return ok ? Result.success() : Result.error("删除失败");
    }
}
