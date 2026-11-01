package com.zht.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.util.Date;

/**
 * 科创板收盘价日频数据（三种加权方式）
 */
@Data
@TableName("kcb_close_daily")
public class KcbCloseDaily {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 交易日期 */
    private Date tradeDate;

    /** 收盘价（算术平均）元 */
    private BigDecimal closeArithmetic;

    /** 收盘价（流通股本加权平均）元 */
    private BigDecimal closeFloatWeighted;

    /** 收盘价（总股本加权平均）元 */
    private BigDecimal closeTotalWeighted;

    /** 参与计算的股票数量 */
    private Integer stockCount;

    private Date createdAt;
    private Date updatedAt;
}
