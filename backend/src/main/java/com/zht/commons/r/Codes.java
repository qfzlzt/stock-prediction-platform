package com.zht.commons.r;

import lombok.Getter;


/**
 * 枚举类 - 多例模式
 */
@Getter
public enum Codes {

    SUCC(200, "成功"),
    FAIL(500, "失败"),
    USER_EXISTS(410, "用户名已经存在"),
    PARAMS_ERROR(414, "参数校验异常"),
    USER_ERROR(411, "用户名错误"),
    LOGIN_FAIL(412, "密码错误"),
    TOKEN_FALSE(413, "Token无效或过期");

    private Integer code;
    private String msg;

    /**
     * 全参构造方法
     * @param code
     * @param msg
     */
    Codes(Integer code, String msg){
        this.code = code;
        this.msg = msg;
    }
}

