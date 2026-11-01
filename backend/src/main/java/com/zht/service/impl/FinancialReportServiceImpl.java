package com.zht.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.CollectionUtils;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import com.github.yulichang.base.MPJBaseServiceImpl;
import com.github.yulichang.wrapper.MPJLambdaWrapper;
import com.zht.dao.FinancialReportDao;
import com.zht.entity.CompanyProfile;
import com.zht.entity.FinancialReport;
import com.zht.entity.FinancialReportVO;
import com.zht.entity.dto.FinancialQuery;
import com.zht.service.FinancialReportService;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.List;

/**
 * 财务状况表(FinancialReport)表服务实现类
 *
 * @author makejava
 * @since 2026-03-08 04:30:48
 */
@Service("financialReportService")
public class FinancialReportServiceImpl extends ServiceImpl<FinancialReportDao, FinancialReport> implements FinancialReportService {


        @Override
        public List<FinancialReportVO> queryList(FinancialQuery query) {
            // 构建连表查询
            MPJLambdaWrapper<FinancialReport> wrapper = new MPJLambdaWrapper<>();

            // 查询财务报告的所有字段
            wrapper.selectAll(FinancialReport.class);

            // 左连接查询公司信息表
            wrapper.leftJoin(CompanyProfile.class, CompanyProfile::getStockcode, FinancialReport::getStockcode);

            // 只查询公司名称（stockname）
            wrapper.selectAs(CompanyProfile::getStockname, FinancialReportVO::getStockname);

            // 添加查询条件
            if (StringUtils.hasText(query.getStockCode())) {
                wrapper.eq(FinancialReport::getStockcode, query.getStockCode());
            }

            if (StringUtils.hasText(query.getReportPeriod())) {
                wrapper.eq(FinancialReport::getReportperiod, query.getReportPeriod());
            }

            if (StringUtils.hasText(query.getReportType())) {
                wrapper.eq(FinancialReport::getReporttype, query.getReportType());
            }

            // 排序
            wrapper.orderByDesc(FinancialReport::getReportperiod)
                    .orderByDesc(FinancialReport::getReporttype);

            // 执行查询，直接返回结果
            return this.baseMapper.selectJoinList(FinancialReportVO.class, wrapper);
        }

    @Override
    public List<FinancialReport> getByStockCode(String stockCode) {


        return this.query().eq("stockCode",stockCode).orderByDesc("reportPeriod").list();
    }
}


