package com.zht.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zht.entity.TechnicalIndicatorLibrary;
import org.apache.ibatis.annotations.Mapper;

/**
 * 技术指标数据库表(TechnicalIndicatorLibrary)表数据库访问层
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@Mapper
public interface TechnicalIndicatorLibraryDao extends BaseMapper<TechnicalIndicatorLibrary> {

    int batchUpsert(java.util.List<TechnicalIndicatorLibrary> list);
}


