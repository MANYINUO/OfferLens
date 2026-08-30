package com.offerlens.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.offerlens.entity.JobDescription;
import com.offerlens.mapper.JobDescriptionMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 职位池（JD 收藏库）
 * 用 content_hash 去重，同一用户同一份 JD 不重复收藏
 */
@Service
public class JobDescriptionService {

    @Autowired
    private JobDescriptionMapper jdMapper;

    /**
     * 收藏一个 JD
     * 如果同一用户已有相同 content_hash 的 JD，返回已存在的那条，不重复插入
     */
    public JobDescription create(Long userId, String company, String position,
                                  String content, String contentHash, String channel) {
        // 先查是否已存在
        LambdaQueryWrapper<JobDescription> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(JobDescription::getUserId, userId)
               .eq(JobDescription::getContentHash, contentHash);
        JobDescription existing = jdMapper.selectOne(wrapper);
        if (existing != null) {
            return existing;
        }
        JobDescription jd = new JobDescription();
        jd.setUserId(userId);
        jd.setCompany(company);
        jd.setPosition(position);
        jd.setContent(content);
        jd.setContentHash(contentHash);
        jd.setChannel(channel);
        jd.setCreatedAt(LocalDateTime.now());
        jdMapper.insert(jd);
        return jd;
    }

    /** 查询用户收藏的所有 JD */
    public List<JobDescription> listByUser(Long userId) {
        LambdaQueryWrapper<JobDescription> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(JobDescription::getUserId, userId)
               .orderByDesc(JobDescription::getCreatedAt);
        return jdMapper.selectList(wrapper);
    }

    /** 根据 id 查询 */
    public JobDescription getById(Long id) {
        return jdMapper.selectById(id);
    }

    /** 更新 JD 信息 */
    public boolean update(Long id, String company, String position, String content, String channel) {
        JobDescription jd = jdMapper.selectById(id);
        if (jd == null) {
            return false;
        }
        if (company != null) jd.setCompany(company);
        if (position != null) jd.setPosition(position);
        if (content != null) jd.setContent(content);
        if (channel != null) jd.setChannel(channel);
        return jdMapper.updateById(jd) > 0;
    }

    /** 删除 JD */
    public boolean delete(Long id) {
        return jdMapper.deleteById(id) > 0;
    }
}
