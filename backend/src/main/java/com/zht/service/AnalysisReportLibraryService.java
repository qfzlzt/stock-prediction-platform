package com.zht.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.zht.entity.AnalysisReportLibrary;
import com.zht.entity.dto.AnalysisQuery;

import java.util.List;

/**
 * 分析报告数据库表(AnalysisReportLibrary)表服务接口
 *
 * @author makejava
 * @since 2026-03-08 04:30:47
 */
public interface AnalysisReportLibraryService extends IService<AnalysisReportLibrary> {

    List<AnalysisReportLibrary> queryList(AnalysisQuery query);
}


