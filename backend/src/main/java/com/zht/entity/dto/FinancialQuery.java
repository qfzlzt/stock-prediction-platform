// FinancialQuery.java
package com.zht.entity.dto;

import lombok.Data;

@Data
public class FinancialQuery {
    
    private String stockCode;
    private String reportPeriod;
    private String reportType;
}