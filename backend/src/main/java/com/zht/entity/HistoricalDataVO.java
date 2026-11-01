package com.zht.entity;

import lombok.Data;

@Data
public class HistoricalDataVO {
    private String date;   // 日期，格式：yyyy-MM-dd
    private Double value;  // 指标值
}