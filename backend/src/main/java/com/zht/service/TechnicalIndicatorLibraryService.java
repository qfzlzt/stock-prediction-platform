package com.zht.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.zht.entity.TechnicalIndicatorLibrary;
import com.zht.entity.dto.TechnicalQuery;

import java.util.List;

/**
 * 技术指标数据库表(TechnicalIndicatorLibrary)表服务接口
 *
 * @author makejava
 * @since 2026-03-08 04:30:49
 */
public interface TechnicalIndicatorLibraryService extends IService<TechnicalIndicatorLibrary> {

    List<TechnicalIndicatorLibrary> queryList(TechnicalQuery query);
}


