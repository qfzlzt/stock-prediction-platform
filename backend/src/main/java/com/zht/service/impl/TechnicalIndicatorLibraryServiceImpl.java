package com.zht.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import com.zht.dao.TechnicalIndicatorLibraryDao;
import com.zht.entity.TechnicalIndicatorLibrary;
import com.zht.entity.dto.TechnicalQuery;
import com.zht.service.TechnicalIndicatorLibraryService;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.List;

/**
 * 技术指标数据库表(TechnicalIndicatorLibrary)表服务实现类
 *
 * @author makejava
 * @since 2026-03-08 04:30:49
 */
@Service("technicalIndicatorLibraryService")
public class TechnicalIndicatorLibraryServiceImpl extends ServiceImpl<TechnicalIndicatorLibraryDao, TechnicalIndicatorLibrary> implements TechnicalIndicatorLibraryService {

    @Override
    public List<TechnicalIndicatorLibrary> queryList(TechnicalQuery query) {
        LambdaQueryWrapper<TechnicalIndicatorLibrary> wrapper = new LambdaQueryWrapper<>();

        if (StringUtils.hasText(query.getStockCode())) {
            wrapper.eq(TechnicalIndicatorLibrary::getStockcode, query.getStockCode());
        }

        if (StringUtils.hasText(query.getTradeDate())) {
            wrapper.eq(TechnicalIndicatorLibrary::getTradedate, query.getTradeDate());
        }

        wrapper.orderByDesc(TechnicalIndicatorLibrary::getTradedate);

        return this.list(wrapper);
    }
}

