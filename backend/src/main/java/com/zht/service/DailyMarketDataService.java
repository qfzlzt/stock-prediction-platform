package com.zht.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.zht.entity.DailyMarketData;
import com.zht.entity.dto.DailyQuery;
import com.zht.entity.HistoricalDataVO;

import java.util.List;

/**
 * 日频市场数据表(DailyMarketData)表服务接口
 *
 * @author makejava
 * @since 2026-03-08 04:30:48
 */
public interface DailyMarketDataService extends IService<DailyMarketData> {

    List<DailyMarketData> queryList(DailyQuery query);

    List<HistoricalDataVO> getHistoricalData(String stockCode, String metric, Integer days);
}


