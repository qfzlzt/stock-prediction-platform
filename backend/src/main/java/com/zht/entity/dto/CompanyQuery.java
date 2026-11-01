// CompanyQuery.java
package com.zht.entity.dto;


import com.zht.commons.PageRequest;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class CompanyQuery extends PageRequest {
    
    private String keyword;
    private String province;
    private String status;
}