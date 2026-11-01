// AnalysisReportLibraryServiceImpl.java
package com.zht.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zht.dao.AnalysisReportLibraryDao;
import com.zht.entity.AnalysisReportLibrary;
import com.zht.entity.dto.AnalysisQuery;
import com.zht.service.AnalysisReportLibraryService;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.List;

@Service
public class AnalysisReportLibraryServiceImpl extends ServiceImpl<AnalysisReportLibraryDao, AnalysisReportLibrary>
        implements AnalysisReportLibraryService {

    @Override
    public List<AnalysisReportLibrary> queryList(AnalysisQuery query) {
        LambdaQueryWrapper<AnalysisReportLibrary> wrapper = new LambdaQueryWrapper<>();

        if (StringUtils.hasText(query.getStockCode())) {
            wrapper.eq(AnalysisReportLibrary::getStockcode, query.getStockCode());
        }

        if (StringUtils.hasText(query.getReportType())) {
            wrapper.eq(AnalysisReportLibrary::getReporttype, query.getReportType());
        }

        if (StringUtils.hasText(query.getReportStatus())) {
            wrapper.eq(AnalysisReportLibrary::getReportstatus, query.getReportStatus());
        }

        wrapper.orderByDesc(AnalysisReportLibrary::getReportgeneratetime);

        return this.list(wrapper);
    }
}