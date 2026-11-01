package com.zht.entity.dto;

import com.zht.entity.DailyMarketData;
import com.zht.entity.RealtimeMarketData;

import java.util.ArrayList;
import java.util.List;

public class WindSyncResult {

    private String tradeDate;
    private int stockCount;
    private int dailySaved;
    private int realtimeSaved;
    private int technicalSaved;
    private List<String> failedStocks = new ArrayList<>();

    /**
     * 返回给前端的日频数据（最近30天）
     */
    private List<DailyMarketData> dailyDataList = new ArrayList<>();

    /**
     * 返回给前端的实时数据（最新时间戳快照）
     */
    private List<RealtimeMarketData> realtimeSnapshotList = new ArrayList<>();

    public String getTradeDate() {
        return tradeDate;
    }

    public void setTradeDate(String tradeDate) {
        this.tradeDate = tradeDate;
    }

    public int getStockCount() {
        return stockCount;
    }

    public void setStockCount(int stockCount) {
        this.stockCount = stockCount;
    }

    public int getDailySaved() {
        return dailySaved;
    }

    public void setDailySaved(int dailySaved) {
        this.dailySaved = dailySaved;
    }

    public int getRealtimeSaved() {
        return realtimeSaved;
    }

    public void setRealtimeSaved(int realtimeSaved) {
        this.realtimeSaved = realtimeSaved;
    }

    public int getTechnicalSaved() {
        return technicalSaved;
    }

    public void setTechnicalSaved(int technicalSaved) {
        this.technicalSaved = technicalSaved;
    }

    public List<String> getFailedStocks() {
        return failedStocks;
    }

    public void setFailedStocks(List<String> failedStocks) {
        this.failedStocks = failedStocks;
    }

    public List<DailyMarketData> getDailyDataList() {
        return dailyDataList;
    }

    public void setDailyDataList(List<DailyMarketData> dailyDataList) {
        this.dailyDataList = dailyDataList;
    }

    public List<RealtimeMarketData> getRealtimeSnapshotList() {
        return realtimeSnapshotList;
    }

    public void setRealtimeSnapshotList(List<RealtimeMarketData> realtimeSnapshotList) {
        this.realtimeSnapshotList = realtimeSnapshotList;
    }
}