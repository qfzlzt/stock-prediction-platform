// DailyQuery.java
package com.zht.entity.dto;

import lombok.Data;

@Data
public class DailyQuery {
    
    private String stockCode;
    private String startDate;
    private String endDate;
    private String sortBy;
    private String sortOrder;
}