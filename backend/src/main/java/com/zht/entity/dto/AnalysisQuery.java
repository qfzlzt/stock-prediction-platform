// AnalysisQuery.java
package com.zht.entity.dto;

import lombok.Data;

@Data
public class AnalysisQuery {
    
    private String stockCode;
    private String reportType;
    private String reportStatus;
}