package com.offerlens.controller;

import com.offerlens.common.Result;
import com.offerlens.entity.InterviewNote;
import com.offerlens.service.InterviewNoteService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * 面试复盘记录接口
 */
@RestController
@RequestMapping("/api/interview-notes")
public class InterviewNoteController {

    @Autowired
    private InterviewNoteService noteService;

    /** 创建复盘记录 */
    @PostMapping
    public Result<InterviewNote> create(@RequestBody Map<String, Object> body) {
        Long userId = Long.valueOf(body.get("userId").toString());
        Long applicationId = Long.valueOf(body.get("applicationId").toString());
        String content = (String) body.get("content");
        return Result.success(noteService.create(userId, applicationId, content));
    }

    /** 查询用户的所有复盘记录 */
    @GetMapping
    public Result<List<InterviewNote>> list(@RequestParam Long userId,
                                            @RequestParam(required = false) Long applicationId) {
        if (applicationId != null) {
            return Result.success(noteService.listByApplication(applicationId));
        }
        return Result.success(noteService.listByUser(userId));
    }

    /** 查询单条复盘 */
    @GetMapping("/{id}")
    public Result<InterviewNote> getById(@PathVariable Long id) {
        InterviewNote note = noteService.getById(id);
        if (note == null) {
            return Result.error("复盘记录不存在");
        }
        return Result.success(note);
    }

    /** 更新复盘 */
    @PutMapping("/{id}")
    public Result<Void> update(@PathVariable Long id, @RequestBody Map<String, String> body) {
        String content = body.get("content");
        boolean ok = noteService.update(id, content);
        return ok ? Result.success() : Result.error("更新失败");
    }

    /** 删除复盘 */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        boolean ok = noteService.delete(id);
        return ok ? Result.success() : Result.error("删除失败");
    }
}
