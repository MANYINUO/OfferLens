package com.offerlens.common;

import java.util.Set;

/**
 * 投递状态枚举 + 合法流转校验
 *
 * 正常推进：applied → viewed → written → first → second → hr → offer
 * 终态：rejected（被拒）、no_response（无回音）、abandoned（放弃）
 *
 * 规则：
 * 1. 只能往前推进一个阶段，不能跳级（applied 不能直接到 first）
 * 2. 任意非终态都可以转到 rejected / no_response / abandoned
 * 3. 终态不能再流转
 */
public enum ApplicationStatus {

    APPLIED("applied"),
    VIEWED("viewed"),
    WRITTEN("written"),
    FIRST("first"),
    SECOND("second"),
    HR("hr"),
    OFFER("offer"),
    REJECTED("rejected"),
    NO_RESPONSE("no_response"),
    ABANDONED("abandoned");

    private final String value;

    ApplicationStatus(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    /** 正常推进的顺序，索引越大越靠后 */
    private static final java.util.List<String> PROGRESS_ORDER = java.util.List.of(
            "applied", "viewed", "written", "first", "second", "hr", "offer"
    );

    /** 终态集合，到了终态就不能再变 */
    private static final Set<String> TERMINAL_STATES = Set.of("rejected", "no_response", "abandoned", "offer");

    /**
     * 校验状态流转是否合法
     * @param from 当前状态
     * @param to 目标状态
     * @return true=合法，false=非法
     */
    public static boolean canTransition(String from, String to) {
        if (from == null || to == null) {
            return false;
        }
        // 终态不能再流转
        if (TERMINAL_STATES.contains(from)) {
            return false;
        }
        // 转到终态：任意非终态都可以
        if (TERMINAL_STATES.contains(to)) {
            return true;
        }
        // 正常推进：只能往前一步
        int fromIdx = PROGRESS_ORDER.indexOf(from);
        int toIdx = PROGRESS_ORDER.indexOf(to);
        if (fromIdx < 0 || toIdx < 0) {
            return false;
        }
        return toIdx == fromIdx + 1;
    }

    /**
     * 获取下一个正常推进的状态
     * @param current 当前状态
     * @return 下一个状态，如果已经是 offer 或终态则返回 null
     */
    public static String nextStatus(String current) {
        int idx = PROGRESS_ORDER.indexOf(current);
        if (idx < 0 || idx >= PROGRESS_ORDER.size() - 1) {
            return null;
        }
        return PROGRESS_ORDER.get(idx + 1);
    }
}
