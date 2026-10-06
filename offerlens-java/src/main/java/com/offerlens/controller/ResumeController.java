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
 *
 * content 最终写入 MySQL 的 TEXT 字段（65,535 字节）。UTF-8 中文占 3 字节，
 * 所以这里按字符数卡在 2 万——约 60,000 字节，留出余量。
 * 该值需与 Python 侧 constants.MAX_TEXT_CHARS、前端 textarea maxlength 保持一致。
 */
@RestController
@RequestMapping("/api/resumes")
public class ResumeController {

    /** 单份简历内容的字符上限 */
    private static final int MAX_CONTENT_CHARS = 20_000;

    @Autowired
    private ResumeService resumeService;

    /** 创建简历 */
    @PostMapping
    public Result<Resume> create(@RequestBody Map<String, Object> body) {
        Long userId = Long.valueOf(body.get("userId").toString());
        String versionName = (String) body.get("versionName");
        String content = (String) body.get("content");
        String tooLong = checkContentLength(content);
        if (tooLong != null) {
            return Result.error(400, tooLong);
        }
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
        String tooLong = checkContentLength(content);
        if (tooLong != null) {
            return Result.error(400, tooLong);
        }
        boolean ok = resumeService.update(id, versionName, content);
        return ok ? Result.success() : Result.error("更新失败");
    }

    /** 删除简历 */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        boolean ok = resumeService.delete(id);
        return ok ? Result.success() : Result.error("删除失败");
    }

    /** 内容超长时返回提示文案，正常返回 null */
    private String checkContentLength(String content) {
        if (content == null) {
            return null;
        }
        if (content.length() > MAX_CONTENT_CHARS) {
            return "简历内容 " + content.length() + " 字，超过 "
                    + MAX_CONTENT_CHARS + " 字上限，请精简后再保存";
        }
        return null;
    }
}
