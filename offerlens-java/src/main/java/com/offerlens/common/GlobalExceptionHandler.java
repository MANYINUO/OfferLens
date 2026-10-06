package com.offerlens.common;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * 全局异常处理。
 *
 * 没有这一层时，未捕获的异常会由 Spring 返回默认的
 * {"timestamp":...,"status":500,"error":"Internal Server Error"}，
 * 前端拿不到 detail/message，只能显示 "Request failed with status code 500"。
 *
 * 这里统一转成 Result，前端 errorMessage() 就能取到中文提示。
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /** 数据库约束：典型场景是简历内容超出 TEXT 字段容量 */
    @ExceptionHandler(DataIntegrityViolationException.class)
    public Result<Void> handleDataIntegrity(DataIntegrityViolationException e) {
        log.warn("数据库约束异常: {}", e.getMessage());
        return Result.error(400, "保存失败：内容超出数据库字段容量，请精简后再试");
    }

    /** 请求体不是合法 JSON，或字段类型对不上 */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public Result<Void> handleUnreadableBody(HttpMessageNotReadableException e) {
        return Result.error(400, "请求内容格式不正确");
    }

    /** 业务校验失败（如非法的状态流转） */
    @ExceptionHandler(IllegalArgumentException.class)
    public Result<Void> handleIllegalArgument(IllegalArgumentException e) {
        return Result.error(400, e.getMessage() == null ? "参数不合法" : e.getMessage());
    }

    /** 兜底：不把堆栈暴露给前端 */
    @ExceptionHandler(Exception.class)
    public Result<Void> handleUnexpected(Exception e) {
        log.error("未处理的异常", e);
        return Result.error(500, "服务内部错误，请稍后重试");
    }
}
