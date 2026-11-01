package com.zht.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zht.entity.RealtimeMarketData;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.Date;
import java.util.List;

/**
 * 实时市场数据表(RealtimeMarketData)表数据库访问层
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@Mapper
public interface RealtimeMarketDataDao extends BaseMapper<RealtimeMarketData> {

    /**
     * 批量插入（使用 ON DUPLICATE KEY UPDATE 避免死锁）
     */
    int batchUpsert(@Param("list") List<RealtimeMarketData> list);

    /**
     * 删除指定股票列表中指定时间戳之前的数据（带限制数量）
     */
    int deleteByStockCodesAndTimestampBeforeWithLimit(@Param("stockCodes") List<String> stockCodes,
                                                        @Param("timestamp") Date timestamp,
                                                        @Param("limit") int limit);

    /**
     * 获取最新时间戳的所有股票实时数据
     */
    List<RealtimeMarketData> selectLatestSnapshot(@Param("stockCodes") List<String> stockCodes);
}