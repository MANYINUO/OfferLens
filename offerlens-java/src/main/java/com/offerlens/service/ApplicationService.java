package com.offerlens.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.offerlens.common.ApplicationStatus;
import com.offerlens.entity.Application;
import com.offerlens.mapper.ApplicationMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 投递记录服务
 * 核心是七阶段状态机：applied → viewed → written → first → second → hr → offer
 * 终态：rejected / no_response / abandoned
 */
@Service
public class ApplicationService {

    @Autowired
    private ApplicationMapper applicationMapper;

    /** 创建一条投递记录，初始状态为 applied */
    public Application create(Long userId, Long jdId, Long resumeId,
                              String company, String position, String channel,
                              String jobType, Integer matchScore, String notes) {
        Application app = new Application();
        app.setUserId(userId);
        app.setJdId(jdId);
        app.setResumeId(resumeId);
        app.setCompany(company);
        app.setPosition(position);
        app.setChannel(channel);
        app.setJobType(jobType);
        app.setMatchScore(matchScore);
        app.setStatus(ApplicationStatus.APPLIED.getValue());
        app.setAppliedAt(LocalDateTime.now());
        app.setLastFollowupAt(LocalDateTime.now());
        app.setNotes(notes);
        applicationMapper.insert(app);
        return app;
    }

    /** 查询用户的所有投递记录 */
    public List<Application> listByUser(Long userId) {
        LambdaQueryWrapper<Application> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Application::getUserId, userId)
               .orderByDesc(Application::getAppliedAt);
        return applicationMapper.selectList(wrapper);
    }

    /** 按状态筛选 */
    public List<Application> listByUserAndStatus(Long userId, String status) {
        LambdaQueryWrapper<Application> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Application::getUserId, userId)
               .eq(Application::getStatus, status)
               .orderByDesc(Application::getAppliedAt);
        return applicationMapper.selectList(wrapper);
    }

    /** 根据 id 查询 */
    public Application getById(Long id) {
        return applicationMapper.selectById(id);
    }

    /**
     * 推进状态（前进一步）
     * applied → viewed → written → first → second → hr → offer
     * @return 推进后的记录，如果已经是终态则返回 null
     */
    public Application advance(Long id) {
        Application app = applicationMapper.selectById(id);
        if (app == null) {
            return null;
        }
        String next = ApplicationStatus.nextStatus(app.getStatus());
        if (next == null) {
            return null; // 已经是 offer 或终态，不能再推进
        }
        app.setStatus(next);
        app.setLastFollowupAt(LocalDateTime.now());
        applicationMapper.updateById(app);
        return app;
    }

    /**
     * 流转到指定状态（含终态）
     * 会校验流转是否合法，非法流转抛出异常
     */
    public Application transition(Long id, String targetStatus) {
        Application app = applicationMapper.selectById(id);
        if (app == null) {
            return null;
        }
        if (!ApplicationStatus.canTransition(app.getStatus(), targetStatus)) {
            throw new IllegalArgumentException(
                    "非法状态流转：" + app.getStatus() + " → " + targetStatus);
        }
        app.setStatus(targetStatus);
        app.setLastFollowupAt(LocalDateTime.now());
        applicationMapper.updateById(app);
        return app;
    }

    /** 更新备注 */
    public boolean updateNotes(Long id, String notes) {
        Application app = applicationMapper.selectById(id);
        if (app == null) {
            return false;
        }
        app.setNotes(notes);
        app.setLastFollowupAt(LocalDateTime.now());
        return applicationMapper.updateById(app) > 0;
    }

    /** 删除投递记录 */
    public boolean delete(Long id) {
        return applicationMapper.deleteById(id) > 0;
    }
}
