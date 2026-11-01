package com.zht.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.zht.entity.RealtimeMarketData;

import java.util.List;

/**
 * 实时市场数据表(RealtimeMarketData)表服务接口
 *
 * @author makejava
 * @since 2026-03-08 04:30:49
 */
public interface RealtimeMarketDataService extends IService<RealtimeMarketData> {

    List<RealtimeMarketData> queryList(String stockCode);
}


