package com.zht.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zht.dao.KcbCloseDailyDao;
import com.zht.entity.KcbCloseDaily;
import com.zht.service.KcbCloseDailyService;
import org.springframework.stereotype.Service;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

@Service
public class KcbCloseDailyServiceImpl
        extends ServiceImpl<KcbCloseDailyDao, KcbCloseDaily>
        implements KcbCloseDailyService {

    private static final SimpleDateFormat SDF = new SimpleDateFormat("yyyy-MM-dd");

    @Override
    public List<KcbCloseDaily> queryByDateRange(String startDate, String endDate) {
        try {
            Date start = (startDate != null && !startDate.isEmpty())
                    ? SDF.parse(startDate) : SDF.parse("2019-07-22");
            Date end = (endDate != null && !endDate.isEmpty())
                    ? SDF.parse(endDate) : new Date();
            return baseMapper.selectByDateRange(start, end);
        } catch (ParseException e) {
            throw new RuntimeException("日期格式错误，请使用 yyyy-MM-dd 格式", e);
        }
    }
}
