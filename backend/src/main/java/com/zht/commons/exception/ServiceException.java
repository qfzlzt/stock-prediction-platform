package com.zht.commons.exception;


import com.zht.commons.r.Codes;
import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 自定义的异常信息
 */
@Getter
@AllArgsConstructor
public class ServiceException extends RuntimeException{

    private Codes codes;
}
