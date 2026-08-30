package com.offerlens.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.offerlens.entity.Resume;
import com.offerlens.mapper.ResumeMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 简历版本管理
 * 一个用户可以有多份简历，每份有版本名（如"Java后端版"、"AI应用版"）
 */
@Service
public class ResumeService {

    @Autowired
    private ResumeMapper resumeMapper;

    /** 创建一份新简历 */
    public Resume create(Long userId, String versionName, String content) {
        Resume resume = new Resume();
        resume.setUserId(userId);
        resume.setVersionName(versionName);
        resume.setContent(content);
        resume.setCreatedAt(LocalDateTime.now());
        resumeMapper.insert(resume);
        return resume;
    }

    /** 查询用户的所有简历版本 */
    public List<Resume> listByUser(Long userId) {
        LambdaQueryWrapper<Resume> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Resume::getUserId, userId)
               .orderByDesc(Resume::getCreatedAt);
        return resumeMapper.selectList(wrapper);
    }

    /** 根据 id 查询单份简历 */
    public Resume getById(Long id) {
        return resumeMapper.selectById(id);
    }

    /** 更新简历内容 */
    public boolean update(Long id, String versionName, String content) {
        Resume resume = resumeMapper.selectById(id);
        if (resume == null) {
            return false;
        }
        if (versionName != null) {
            resume.setVersionName(versionName);
        }
        if (content != null) {
            resume.setContent(content);
        }
        return resumeMapper.updateById(resume) > 0;
    }

    /** 删除简历 */
    public boolean delete(Long id) {
        return resumeMapper.deleteById(id) > 0;
    }
}
