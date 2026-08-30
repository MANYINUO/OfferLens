package com.offerlens.controller;

import com.offerlens.common.Result;
import com.offerlens.entity.JobDescription;
import com.offerlens.service.JobDescriptionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 职位池（JD 收藏库）接口
 */
@RestController
@RequestMapping("/api/jobs")
public class JobDescriptionController {

    @Autowired
    private JobDescriptionService jdService;

    /** 收藏 JD（自动去重） */
    @PostMapping
    public Result<JobDescription> create(@RequestBody Map<String, Object> body) {
        Long userId = Long.valueOf(body.get("userId").toString());
        String company = (String) body.get("company");
        String position = (String) body.get("position");
        String content = (String) body.get("content");
        String contentHash = (String) body.get("contentHash");
        String channel = (String) body.get("channel");
        return Result.success(jdService.create(userId, company, position, content, contentHash, channel));
    }

    /** 查询用户收藏的所有 JD */
    @GetMapping
    public Result<List<JobDescription>> list(@RequestParam Long userId) {
        return Result.success(jdService.listByUser(userId));
    }

    /** 查询单个 JD */
    @GetMapping("/{id}")
    public Result<JobDescription> getById(@PathVariable Long id) {
        JobDescription jd = jdService.getById(id);
        if (jd == null) {
            return Result.error("职位不存在");
        }
        return Result.success(jd);
    }

    /** 更新 JD */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        String company = (String) body.get("company");
        String position = (String) body.get("position");
        String content = (String) body.get("content");
        String channel = (String) body.get("channel");
        boolean ok = jdService.update(id, company, position, content, channel);
        return ok ? Result.success() : Result.error("更新失败");
    }

    /** 删除 JD */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        boolean ok = jdService.delete(id);
        return ok ? Result.success() : Result.error("删除失败");
    }
}
