package com.zht.entity.dto;

import java.util.List;

public class WindSyncRequest {

    private String tradeDate;
    private List<String> stockCodes;
    private Boolean syncDaily = true;
    private Boolean syncRealtime = true;
    private Boolean syncTechnical = true;
    private String predictionResult = "待预测";
    private String algorithmVersion = "v1.0_LSTM";

    /**
     * 日频数据查询天数（默认30天）
     */
    private Integer days = 60;

    /**
     * 实时数据保留分钟数（默认30分钟）
     */
    private Integer realtimeRetainMinutes = 30;

    public String getTradeDate() {
        return tradeDate;
    }

    public void setTradeDate(String tradeDate) {
        this.tradeDate = tradeDate;
    }

    public List<String> getStockCodes() {
        return stockCodes;
    }

    public void setStockCodes(List<String> stockCodes) {
        this.stockCodes = stockCodes;
    }

    public Boolean getSyncDaily() {
        return syncDaily;
    }

    public void setSyncDaily(Boolean syncDaily) {
        this.syncDaily = syncDaily;
    }

    public Boolean getSyncRealtime() {
        return syncRealtime;
    }

    public void setSyncRealtime(Boolean syncRealtime) {
        this.syncRealtime = syncRealtime;
    }

    public Boolean getSyncTechnical() {
        return syncTechnical;
    }

    public void setSyncTechnical(Boolean syncTechnical) {
        this.syncTechnical = syncTechnical;
    }

    public String getPredictionResult() {
        return predictionResult;
    }

    public void setPredictionResult(String predictionResult) {
        this.predictionResult = predictionResult;
    }

    public String getAlgorithmVersion() {
        return algorithmVersion;
    }

    public void setAlgorithmVersion(String algorithmVersion) {
        this.algorithmVersion = algorithmVersion;
    }

    public Integer getDays() {
        return days;
    }

    public void setDays(Integer days) {
        this.days = days;
    }

    public Integer getRealtimeRetainMinutes() {
        return realtimeRetainMinutes;
    }

    public void setRealtimeRetainMinutes(Integer realtimeRetainMinutes) {
        this.realtimeRetainMinutes = realtimeRetainMinutes;
    }
}