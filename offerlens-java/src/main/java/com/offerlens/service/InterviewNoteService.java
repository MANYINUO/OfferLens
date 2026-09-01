package com.offerlens.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.offerlens.entity.InterviewNote;
import com.offerlens.mapper.InterviewNoteMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 面试复盘记录服务
 */
@Service
public class InterviewNoteService {

    @Autowired
    private InterviewNoteMapper noteMapper;

    /** 创建一条复盘记录 */
    public InterviewNote create(Long userId, Long applicationId, String content) {
        InterviewNote note = new InterviewNote();
        note.setUserId(userId);
        note.setApplicationId(applicationId);
        note.setContent(content);
        note.setCreatedAt(LocalDateTime.now());
        noteMapper.insert(note);
        return note;
    }

    /** 查询用户的所有复盘记录 */
    public List<InterviewNote> listByUser(Long userId) {
        LambdaQueryWrapper<InterviewNote> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(InterviewNote::getUserId, userId)
               .orderByDesc(InterviewNote::getCreatedAt);
        return noteMapper.selectList(wrapper);
    }

    /** 查询某条投递的复盘记录 */
    public List<InterviewNote> listByApplication(Long applicationId) {
        LambdaQueryWrapper<InterviewNote> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(InterviewNote::getApplicationId, applicationId)
               .orderByDesc(InterviewNote::getCreatedAt);
        return noteMapper.selectList(wrapper);
    }

    /** 根据 id 查询 */
    public InterviewNote getById(Long id) {
        return noteMapper.selectById(id);
    }

    /** 更新复盘内容 */
    public boolean update(Long id, String content) {
        InterviewNote note = noteMapper.selectById(id);
        if (note == null) {
            return false;
        }
        note.setContent(content);
        return noteMapper.updateById(note) > 0;
    }

    /** 删除复盘记录 */
    public boolean delete(Long id) {
        return noteMapper.deleteById(id) > 0;
    }
}
