package com.offerlens.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * JD 收藏库实体
 */
@Data
@TableName("job_description")
public class JobDescription {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private String company;

    private String position;

    private String content;

    private String contentHash;

    private String channel;

    private LocalDateTime createdAt;
}
