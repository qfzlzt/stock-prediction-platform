package com.zht.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.zht.entity.KcbCloseDaily;

import java.util.List;

public interface KcbCloseDailyService extends IService<KcbCloseDaily> {

    /**
     * 按日期范围查询科创板收盘价指标
     *
     * @param startDate 开始日期，格式 yyyy-MM-dd，为 null 时默认科创板开板日 2019-07-22
     * @param endDate   结束日期，格式 yyyy-MM-dd，为 null 时默认今天
     */
    List<KcbCloseDaily> queryByDateRange(String startDate, String endDate);
}
