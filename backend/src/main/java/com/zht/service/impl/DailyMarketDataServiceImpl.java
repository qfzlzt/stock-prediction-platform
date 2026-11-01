package com.zht.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import com.zht.dao.DailyMarketDataDao;
import com.zht.entity.DailyMarketData;
import com.zht.entity.HistoricalDataVO;
import com.zht.entity.dto.DailyQuery;
import com.zht.service.DailyMarketDataService;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import javax.annotation.Resource;
import java.time.LocalDate;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 日频市场数据表(DailyMarketData)表服务实现类
 *
 * @author makejava
 * @since 2026-03-08 04:30:48
 */
@Service("dailyMarketDataService")
public class DailyMarketDataServiceImpl extends ServiceImpl<DailyMarketDataDao, DailyMarketData> implements DailyMarketDataService {

    @Resource
    private DailyMarketDataDao dailyMarketDataDao;

    @Override
    public List<DailyMarketData> queryList(DailyQuery query) {
        LambdaQueryWrapper<DailyMarketData> wrapper = new LambdaQueryWrapper<>();

        if (StringUtils.hasText(query.getStockCode())) {
            wrapper.eq(DailyMarketData::getStockCode, query.getStockCode());
        }

        if (StringUtils.hasText(query.getStartDate())) {
            wrapper.ge(DailyMarketData::getTradeDate, query.getStartDate());
        }

        if (StringUtils.hasText(query.getEndDate())) {
            wrapper.le(DailyMarketData::getTradeDate, query.getEndDate());
        }

        // 排序
        if (StringUtils.hasText(query.getSortBy())) {
            if ("asc".equalsIgnoreCase(query.getSortOrder())) {
                wrapper.orderByAsc(DailyMarketData::getTradeDate);
            } else {
                wrapper.orderByDesc(DailyMarketData::getTradeDate);
            }
        } else {
            wrapper.orderByDesc(DailyMarketData::getTradeDate);
        }

        return this.list(wrapper);
    }

    public List<HistoricalDataVO> getHistoricalData(String stockCode, String metric, Integer days) {
        // 1. 计算起始日期
        LocalDate endDate = LocalDate.now();
        LocalDate startDate = endDate.minusDays(days);

        // 2. 查询历史数据
        List<DailyMarketData> dataList = dailyMarketDataDao.selectByStockCodeAndDateRange(
                stockCode, startDate, endDate);

        // 3. 转换为前端需要的格式
        return dataList.stream()
                .map(data -> {
                    HistoricalDataVO vo = new HistoricalDataVO();
                    vo.setDate(data.getTradeDate().toString());
                    // 根据 metric 字段名动态获取值
                    Object value = getMetricValue(data, metric);
                    vo.setValue(value instanceof Number ? ((Number) value).doubleValue() : 0.0);
                    return vo;
                })
                .sorted(Comparator.comparing(HistoricalDataVO::getDate))
                .collect(Collectors.toList());
    }

    private Object getMetricValue(DailyMarketData data, String metric) {
        switch (metric) {
            case "pe": return data.getPe();
            case "pb": return data.getPb();
            case "pctChg": return data.getPctChg();
            case "ev": return data.getEv();
            case "mktCapFloat": return data.getMktCapFloat();
            case "totalShares": return data.getTotalShares();
            case "shareIssuingMkt": return data.getShareIssuingMkt();
            case "chg": return data.getChg();
            case "vwap": return data.getVwap();
            case "volume": return data.getVolume();
            case "amt": return data.getAmt();
            case "turn": return data.getTurn();
            case "volRatio": return data.getVolRatio();
            case "high": return data.getHigh();
            case "low": return data.getLow();
            case "open": return data.getOpen();
            case "close": return data.getClose();
            case "preClose": return data.getPreClose();
            case "adjfactor": return data.getAdjfactor();
            default: return null;
        }
    }
}

