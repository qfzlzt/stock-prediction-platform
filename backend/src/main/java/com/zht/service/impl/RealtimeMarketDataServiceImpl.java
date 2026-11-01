package com.zht.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import com.zht.constants.StockPoolConstants;
import com.zht.dao.RealtimeMarketDataDao;
import com.zht.entity.RealtimeMarketData;
import com.zht.service.RealtimeMarketDataService;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * 实时市场数据表(RealtimeMarketData)表服务实现类
 *
 * @author makejava
 * @since 2026-03-08 04:30:49
 */
@Service("realtimeMarketDataService")
public class RealtimeMarketDataServiceImpl extends ServiceImpl<RealtimeMarketDataDao, RealtimeMarketData> implements RealtimeMarketDataService {

    @Override
    public List<RealtimeMarketData> queryList(String stockCode) {
        if (StringUtils.hasText(stockCode)) {
            // 如果指定了股票代码，则查询该股票的最新一条数据
            LambdaQueryWrapper<RealtimeMarketData> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(RealtimeMarketData::getStockcode, stockCode);
            wrapper.orderByDesc(RealtimeMarketData::getDatatimestamp);
            wrapper.last("limit 1");
            return this.list(wrapper);
        } else {
            // 第一步：查询每个股票的最新时间戳
            List<RealtimeMarketData> latestRecords = new ArrayList<>();
            for (String code : StockPoolConstants.DEFAULT_STOCK_CODES) {
                LambdaQueryWrapper<RealtimeMarketData> wrapper = new LambdaQueryWrapper<>();
                wrapper.eq(RealtimeMarketData::getStockcode, code);
                wrapper.orderByDesc(RealtimeMarketData::getDatatimestamp);
                wrapper.last("limit 1");
                RealtimeMarketData record = this.getOne(wrapper);
                if (record != null) {
                    latestRecords.add(record);
                }
            }
            return latestRecords;
        }
    }
}

