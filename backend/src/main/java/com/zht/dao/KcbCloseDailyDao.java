package com.zht.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zht.entity.KcbCloseDaily;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.Date;
import java.util.List;

@Mapper
public interface KcbCloseDailyDao extends BaseMapper<KcbCloseDaily> {

    Date selectMaxTradeDate();

    List<KcbCloseDaily> selectByDateRange(
            @Param("startDate") Date startDate,
            @Param("endDate")   Date endDate
    );

    int upsert(@Param("item") KcbCloseDaily item);
}
