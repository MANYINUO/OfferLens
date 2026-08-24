package com.offerlens.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 投递记录实体（含七阶段状态机）
 * 状态流转：applied → viewed → written → first → second → hr → offer
 * 终态：rejected / no_response / abandoned
 */
@Data
@TableName("application")
public class Application {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private Long jdId;

    private Long resumeId;

    private String company;

    private String position;

    private String channel;

    private String jobType;

    private Integer matchScore;

    /** 投递状态：applied/viewed/written/first/second/hr/offer/rejected/no_response/abandoned */
    private String status;

    private LocalDateTime appliedAt;

    private LocalDateTime lastFollowupAt;

    private String notes;
}
