package com.offerlens.controller;

import com.offerlens.common.Result;
import com.offerlens.entity.Resume;
import com.offerlens.service.ResumeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 简历版本管理接口
 */
@RestController
@RequestMapping("/api/resumes")
public class ResumeController {

    @Autowired
    private ResumeService resumeService;

    /** 创建简历 */
    @PostMapping
    public Result<Resume> create(@RequestBody Map<String, Object> body) {
        Long userId = Long.valueOf(body.get("userId").toString());
        String versionName = (String) body.get("versionName");
        String content = (String) body.get("content");
        return Result.success(resumeService.create(userId, versionName, content));
    }

    /** 查询用户的所有简历版本 */
    @GetMapping
    public Result<List<Resume>> list(@RequestParam Long userId) {
        return Result.success(resumeService.listByUser(userId));
    }

    /** 查询单份简历 */
    @GetMapping("/{id}")
    public Result<Resume> getById(@PathVariable Long id) {
        Resume resume = resumeService.getById(id);
        if (resume == null) {
            return Result.error("简历不存在");
        }
        return Result.success(resume);
    }

    /** 更新简历 */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        String versionName = (String) body.get("versionName");
        String content = (String) body.get("content");
        boolean ok = resumeService.update(id, versionName, content);
        return ok ? Result.success() : Result.error("更新失败");
    }

    /** 删除简历 */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        boolean ok = resumeService.delete(id);
        return ok ? Result.success() : Result.error("删除失败");
    }
}
