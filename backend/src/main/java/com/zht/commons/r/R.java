package com.zht.commons.r;

import lombok.Data;
import lombok.experimental.Accessors;

import java.io.Serializable;

@Data
@Accessors(chain = true)
public class R<T> implements Serializable {

    /**
     * 响应码
     */
    private Integer code;

    /**
     * 响应内容
     */
    private String msg;

    /**
     * 响应数据
     */
    private T data;

    /**
     * 生成一个代表成功的R对象
     * @return
     */
    public static <S> R<S> succ(S data){
        return new R<S>().setCode(Codes.SUCC.getCode())
                .setMsg(Codes.SUCC.getMsg())
                .setData(data);
    }

    /**
     * 生成一个代表成功的R对象，不带数据部分
     * @return
     * @param <S>
     */
    public static <S> R<S> succ(){
        return succ(null);
    }

    /**
     * 生成一个失败的R对象
     * @return
     * @param <S>
     */
    public static <S> R<S> fail(Codes codes) {
        return fail(codes, null);
    }

    /**
     * 生成一个失败的R对象，带数据
     * @return
     * @param <S>
     */
    public static <S> R<S> fail(Codes codes, S data) {
        return new R<S>()
                .setCode(codes.getCode())
                .setMsg(codes.getMsg())
                .setData(data);
    }
}
