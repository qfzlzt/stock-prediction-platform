package com.zht.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.github.yulichang.base.MPJBaseMapper;
import com.zht.entity.FinancialReport;
import org.apache.ibatis.annotations.Mapper;

/**
 * 财务状况表(FinancialReport)表数据库访问层
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@Mapper
public interface FinancialReportDao extends MPJBaseMapper<FinancialReport> {

}

