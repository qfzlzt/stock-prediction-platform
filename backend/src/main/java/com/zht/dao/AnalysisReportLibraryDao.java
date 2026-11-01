package com.zht.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zht.entity.AnalysisReportLibrary;
import org.apache.ibatis.annotations.Mapper;

/**
 * 分析报告数据库表(AnalysisReportLibrary)表数据库访问层
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@Mapper
public interface AnalysisReportLibraryDao extends BaseMapper<AnalysisReportLibrary> {

}

