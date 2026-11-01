package com.zht.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.zht.entity.FinancialReport;
import com.zht.entity.FinancialReportVO;
import com.zht.entity.dto.FinancialQuery;

import java.util.List;

/**
 * 财务状况表(FinancialReport)表服务接口
 *
 * @author makejava
 * @since 2026-03-08 04:30:48
 */
public interface FinancialReportService extends IService<FinancialReport> {

    List<FinancialReportVO> queryList(FinancialQuery query);

    List<FinancialReport> getByStockCode(String stockCode);
}

