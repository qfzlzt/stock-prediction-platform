package com.zht.entity;


import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.activerecord.Model;
import java.io.Serializable;
import java.util.Date;

/**
 * 技术指标数据库表(TechnicalIndicatorLibrary)表实体类
 *
 * @author makejava
 * @since 2026-03-24 23:23:12
 */
@SuppressWarnings("serial")
@TableName("technical_indicator_library")
public class TechnicalIndicatorLibrary extends Model<TechnicalIndicatorLibrary> {
//主键ID
    private Long id;
//A股代码
    @TableField("stockCode")
    private String stockcode;
//交易日期
    @TableField("tradeDate")
    private Date tradedate;
//1日收益率
    @TableField("ret_1_calc")
    private Double ret1Calc;
//5日收益率
    @TableField("ret_5")
    private Double ret5;
//20日收益率
    @TableField("ret_20")
    private Double ret20;
//60日收益率
    @TableField("ret_60")
    private Double ret60;
//6日相对强弱指标
    @TableField("rsi_6")
    private Double rsi6;
//14日相对强弱指标
    @TableField("rsi_14")
    private Double rsi14;
//MACD主线
    private Double macd;
//MACD信号线
    private Double macdSignal;
//MACD柱值
    private Double macdHist;
//布林带中轨
    private Double bbMid;
//布林带标准差
    private Double bbStd;
//布林带上轨
    private Double bbUpper;
//布林带下轨
    private Double bbLower;
//布林带宽度
    private Double bbWidth;
//布林带位置
    private Double bbPos;
//真实波幅
    private Double tr;
//14日平均真实波幅
    @TableField("atr_14")
    private Double atr14;
//ATR相对比例
    private Double atrPct;
//20日波动率
    @TableField("vol_20")
    private Double vol20;
//60日波动率
    @TableField("vol_60")
    private Double vol60;
//5日均线
    private Double ma5;
//10日均线
    private Double ma10;
//20日均线
    private Double ma20;
//60日均线
    private Double ma60;
//5日均线偏离率
    private Double ma5Dev;
//20日均线偏离率
    private Double ma20Dev;
//5日平均成交量
    private Double volumeMa5;
//20日平均成交量
    private Double volumeMa20;
//成交量放大倍数
    private Double volSurge;
//价量相关系数
    private Double priceVolCorr;
//计算时间
    private Date calculatedat;
//创建时间
    private Date createdat;
//更新时间
    private Date updatedat;


    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getStockcode() {
        return stockcode;
    }

    public void setStockcode(String stockcode) {
        this.stockcode = stockcode;
    }

    public Date getTradedate() {
        return tradedate;
    }

    public void setTradedate(Date tradedate) {
        this.tradedate = tradedate;
    }

    public Double getRet1Calc() {
        return ret1Calc;
    }

    public void setRet1Calc(Double ret1Calc) {
        this.ret1Calc = ret1Calc;
    }

    public Double getRet5() {
        return ret5;
    }

    public void setRet5(Double ret5) {
        this.ret5 = ret5;
    }

    public Double getRet20() {
        return ret20;
    }

    public void setRet20(Double ret20) {
        this.ret20 = ret20;
    }

    public Double getRet60() {
        return ret60;
    }

    public void setRet60(Double ret60) {
        this.ret60 = ret60;
    }

    public Double getRsi6() {
        return rsi6;
    }

    public void setRsi6(Double rsi6) {
        this.rsi6 = rsi6;
    }

    public Double getRsi14() {
        return rsi14;
    }

    public void setRsi14(Double rsi14) {
        this.rsi14 = rsi14;
    }

    public Double getMacd() {
        return macd;
    }

    public void setMacd(Double macd) {
        this.macd = macd;
    }

    public Double getMacdSignal() {
        return macdSignal;
    }

    public void setMacdSignal(Double macdSignal) {
        this.macdSignal = macdSignal;
    }

    public Double getMacdHist() {
        return macdHist;
    }

    public void setMacdHist(Double macdHist) {
        this.macdHist = macdHist;
    }

    public Double getBbMid() {
        return bbMid;
    }

    public void setBbMid(Double bbMid) {
        this.bbMid = bbMid;
    }

    public Double getBbStd() {
        return bbStd;
    }

    public void setBbStd(Double bbStd) {
        this.bbStd = bbStd;
    }

    public Double getBbUpper() {
        return bbUpper;
    }

    public void setBbUpper(Double bbUpper) {
        this.bbUpper = bbUpper;
    }

    public Double getBbLower() {
        return bbLower;
    }

    public void setBbLower(Double bbLower) {
        this.bbLower = bbLower;
    }

    public Double getBbWidth() {
        return bbWidth;
    }

    public void setBbWidth(Double bbWidth) {
        this.bbWidth = bbWidth;
    }

    public Double getBbPos() {
        return bbPos;
    }

    public void setBbPos(Double bbPos) {
        this.bbPos = bbPos;
    }

    public Double getTr() {
        return tr;
    }

    public void setTr(Double tr) {
        this.tr = tr;
    }

    public Double getAtr14() {
        return atr14;
    }

    public void setAtr14(Double atr14) {
        this.atr14 = atr14;
    }

    public Double getAtrPct() {
        return atrPct;
    }

    public void setAtrPct(Double atrPct) {
        this.atrPct = atrPct;
    }

    public Double getVol20() {
        return vol20;
    }

    public void setVol20(Double vol20) {
        this.vol20 = vol20;
    }

    public Double getVol60() {
        return vol60;
    }

    public void setVol60(Double vol60) {
        this.vol60 = vol60;
    }

    public Double getMa5() {
        return ma5;
    }

    public void setMa5(Double ma5) {
        this.ma5 = ma5;
    }

    public Double getMa10() {
        return ma10;
    }

    public void setMa10(Double ma10) {
        this.ma10 = ma10;
    }

    public Double getMa20() {
        return ma20;
    }

    public void setMa20(Double ma20) {
        this.ma20 = ma20;
    }

    public Double getMa60() {
        return ma60;
    }

    public void setMa60(Double ma60) {
        this.ma60 = ma60;
    }

    public Double getMa5Dev() {
        return ma5Dev;
    }

    public void setMa5Dev(Double ma5Dev) {
        this.ma5Dev = ma5Dev;
    }

    public Double getMa20Dev() {
        return ma20Dev;
    }

    public void setMa20Dev(Double ma20Dev) {
        this.ma20Dev = ma20Dev;
    }

    public Double getVolumeMa5() {
        return volumeMa5;
    }

    public void setVolumeMa5(Double volumeMa5) {
        this.volumeMa5 = volumeMa5;
    }

    public Double getVolumeMa20() {
        return volumeMa20;
    }

    public void setVolumeMa20(Double volumeMa20) {
        this.volumeMa20 = volumeMa20;
    }

    public Double getVolSurge() {
        return volSurge;
    }

    public void setVolSurge(Double volSurge) {
        this.volSurge = volSurge;
    }

    public Double getPriceVolCorr() {
        return priceVolCorr;
    }

    public void setPriceVolCorr(Double priceVolCorr) {
        this.priceVolCorr = priceVolCorr;
    }

    public Date getCalculatedat() {
        return calculatedat;
    }

    public void setCalculatedat(Date calculatedat) {
        this.calculatedat = calculatedat;
    }

    public Date getCreatedat() {
        return createdat;
    }

    public void setCreatedat(Date createdat) {
        this.createdat = createdat;
    }

    public Date getUpdatedat() {
        return updatedat;
    }

    public void setUpdatedat(Date updatedat) {
        this.updatedat = updatedat;
    }

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

