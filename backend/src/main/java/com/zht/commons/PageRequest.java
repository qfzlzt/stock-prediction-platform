// PageRequest.java
package com.zht.commons;

import lombok.Data;

@Data
public class PageRequest {
    
    private Integer pageNum = 1;
    private Integer pageSize = 10;
}