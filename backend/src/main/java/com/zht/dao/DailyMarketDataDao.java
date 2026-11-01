package com.zht.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zht.entity.DailyMarketData;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.time.LocalDate;
import java.util.Date;
import java.util.List;

/**
 * 日频市场数据表(DailyMarketData)表数据库访问层
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@Mapper
public interface DailyMarketDataDao extends BaseMapper<DailyMarketData> {

    int batchUpsert(@Param("list") List<DailyMarketData> list);

    /**
     * 删除指定日期之前的数据
     */
    int deleteByTradeDateBefore(@Param("date") Date date);

    /**
     * 删除指定股票、指定日期之前的数据
     */
    int deleteByStockCodesAndTradeDateBefore(@Param("stockCodes") List<String> stockCodes,
                                              @Param("date") Date date);

    /**
     * 查询指定股票、指定日期范围内的日频数据
     */
    List<DailyMarketData> selectByStockCodesAndDateRange(@Param("stockCodes") List<String> stockCodes,
                                                          @Param("startDate") Date startDate,
                                                          @Param("endDate") Date endDate);

    List<DailyMarketData> selectByStockCodeAndDateRange(String stockCode, LocalDate startDate, LocalDate endDate);
}