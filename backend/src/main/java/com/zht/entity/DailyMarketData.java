package com.zht.entity;


import com.baomidou.mybatisplus.extension.activerecord.Model;
import lombok.Data;

import java.io.Serializable;
import java.util.Date;

/**
 * 日频数据表(DailyMarketData)表实体类
 *
 * @author makejava
 * @since 2026-03-20 19:05:37
 */
@Data
@SuppressWarnings("serial")
public class DailyMarketData extends Model<DailyMarketData> {
//主键ID
    private Long id;
//股票代码，如 688041.SH
    private String stockCode;
//交易日期
    private Date tradeDate;
//市盈率PE（最新年报 LYR）
    private Double pe;
//市净率PB（当年一季）
    private Double pb;
//涨跌幅（%）
    private Double pctChg;
//总市值1（元）
    private Double ev;
//流通市值（含限售股，元，原始币种）
    private Double mktCapFloat;
//总股本（股）
    private Double totalShares;
//流通股本（含限售股，股）
    private Double shareIssuingMkt;
//涨停价
    private Double maxup;
//跌停价
    private Double maxdown;
//涨跌
    private Double chg;
//均价
    private Double vwap;
//成交量
    private Double volume;
//成交额（元）
    private Double amt;
//换手率
    private Double turn;
//量比（参数5）
    private Double volRatio;
//最高价
    private Double high;
//最低价
    private Double low;
//开盘价
    private Double open;
//收盘价
    private Double close;
//前收盘价
    private Double preClose;
//复权因子
    private Double adjfactor;
//创建时间
    private Date createTime;
//更新时间
    private Date updateTime;



    /**
     * 获取主键值
     *
     * @return 主键值
     */
    @Override
    public Serializable pkVal() {
        return this.id;
    }
}

