package com.zht.entity;

import java.math.BigDecimal;
import java.util.Date;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.extension.activerecord.Model;
import lombok.Data;

import java.io.Serializable;

/**
 * 财务状况表(FinancialReport)表实体类
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@SuppressWarnings("serial")
@Data
public class FinancialReport extends Model<FinancialReport> {
    //A股代码
    @TableId(type = IdType.INPUT)
    private String stockcode;
    //报告年份
    private String reportperiod;
    //报告类型(Q1-一季报,Q2-二季报,S1-半年报,Q3-三季报,Q4-四季报,A-年报)
    private Object reporttype;
    //基本每股收益(元)
    private BigDecimal basiceps;
    //每股净资产(元)
    private BigDecimal netassetspershare;
    //资本公积金(元)
    private BigDecimal capitalreserve;
    //每股未分配利润(元)
    private BigDecimal undistributedprofitpershare;
    //每股现金净额(元)
    private BigDecimal operatingcashflowpershare;
    //营业总收入(元)
    private BigDecimal totaloperatingrevenue;
    //净利润(元)
    private BigDecimal netprofitattributable;
    //营业总收入同比增长(%)
    private BigDecimal totaloperatingrevenueyoy;
    //净资产收益率(%)
    private BigDecimal roe;
    //毛利率(%)
    private BigDecimal grossmargin;

    //创建时间
    private Date createdat;
    //更新时间
    private Date updatedat;
    /**
     * 获取主键值
     *
     * @return 主键值
     */
    @Override
    public Serializable pkVal() {
        return this.stockcode;
    }
    }

