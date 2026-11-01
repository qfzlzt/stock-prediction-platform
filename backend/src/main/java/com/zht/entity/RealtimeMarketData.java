package com.zht.entity;

import java.math.BigDecimal;
import java.util.Date;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.extension.activerecord.Model;
import java.io.Serializable;

/**
 * 实时市场数据表(RealtimeMarketData)表实体类
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@SuppressWarnings("serial")
public class RealtimeMarketData extends Model<RealtimeMarketData> {
    //主键ID
    @TableId(type = IdType.AUTO)
    private Long id;
    //A股代码
    private String stockcode;
    //最新价(元)
    private BigDecimal latestprice;
    //涨跌(元)
    private BigDecimal pricechange;
    //涨幅(%)
    private BigDecimal pricechangerate;
    //均价(元)
    private BigDecimal averageprice;
    //成交量(手)
    private BigDecimal totalvolume;
    //成交额(元)
    private BigDecimal turnover;
    //换手率(%)
    private BigDecimal turnoverrate;
    //量比
    private BigDecimal volumeratio;
    //最高价(元)
    private BigDecimal highestprice;
    //最低价(元)
    private BigDecimal lowestprice;
    //开盘价(元)
    private BigDecimal openingprice;
    //前收盘价(元)
    private BigDecimal precloseprice;
    //收盘价(元)
    private BigDecimal closeprice;
    //复权因子
    private BigDecimal adjfactor;
    //数据时间戳
    private Date datatimestamp;
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

    public BigDecimal getLatestprice() {
        return latestprice;
    }

    public void setLatestprice(BigDecimal latestprice) {
        this.latestprice = latestprice;
    }

    public BigDecimal getPricechange() {
        return pricechange;
    }

    public void setPricechange(BigDecimal pricechange) {
        this.pricechange = pricechange;
    }

    public BigDecimal getPricechangerate() {
        return pricechangerate;
    }

    public void setPricechangerate(BigDecimal pricechangerate) {
        this.pricechangerate = pricechangerate;
    }

    public BigDecimal getAverageprice() {
        return averageprice;
    }

    public void setAverageprice(BigDecimal averageprice) {
        this.averageprice = averageprice;
    }

    public BigDecimal getTotalvolume() {
        return totalvolume;
    }

    public void setTotalvolume(BigDecimal totalvolume) {
        this.totalvolume = totalvolume;
    }

    public BigDecimal getTurnover() {
        return turnover;
    }

    public void setTurnover(BigDecimal turnover) {
        this.turnover = turnover;
    }

    public BigDecimal getTurnoverrate() {
        return turnoverrate;
    }

    public void setTurnoverrate(BigDecimal turnoverrate) {
        this.turnoverrate = turnoverrate;
    }

    public BigDecimal getVolumeratio() {
        return volumeratio;
    }

    public void setVolumeratio(BigDecimal volumeratio) {
        this.volumeratio = volumeratio;
    }

    public BigDecimal getHighestprice() {
        return highestprice;
    }

    public void setHighestprice(BigDecimal highestprice) {
        this.highestprice = highestprice;
    }

    public BigDecimal getLowestprice() {
        return lowestprice;
    }

    public void setLowestprice(BigDecimal lowestprice) {
        this.lowestprice = lowestprice;
    }

    public BigDecimal getOpeningprice() {
        return openingprice;
    }

    public void setOpeningprice(BigDecimal openingprice) {
        this.openingprice = openingprice;
    }

    public BigDecimal getPrecloseprice() {
        return precloseprice;
    }

    public void setPrecloseprice(BigDecimal precloseprice) {
        this.precloseprice = precloseprice;
    }

    public BigDecimal getCloseprice() {
        return closeprice;
    }

    public void setCloseprice(BigDecimal closeprice) {
        this.closeprice = closeprice;
    }

    public BigDecimal getAdjfactor() {
        return adjfactor;
    }

    public void setAdjfactor(BigDecimal adjfactor) {
        this.adjfactor = adjfactor;
    }

    public Date getDatatimestamp() {
        return datatimestamp;
    }

    public void setDatatimestamp(Date datatimestamp) {
        this.datatimestamp = datatimestamp;
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

