package com.zht.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class FinancialReportVO extends FinancialReport {
    
    /**
     * 股票名称（来自CompanyProfile）
     */
    private String stockname;
}