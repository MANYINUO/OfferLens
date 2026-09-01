package com.offerlens.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 面试复盘记录
 * 记录每次面试被问了什么、答得怎么样，用于反哺面试题预测
 */
@Data
@TableName("interview_note")
public class InterviewNote {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private Long applicationId;

    private String content;

    private LocalDateTime createdAt;
}
