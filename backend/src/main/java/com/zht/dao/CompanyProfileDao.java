package com.zht.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zht.entity.CompanyProfile;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 公司概况表(CompanyProfile)表数据库访问层
 *
 * @author makejava
 * @since 2026-03-08 04:46:17
 */
@Mapper
public interface CompanyProfileDao extends BaseMapper<CompanyProfile> {


    @Select("SELECT DISTINCT stockcode, stockname FROM company_profile WHERE stockcode IS NOT NULL")
    List<CompanyProfile> selectSimpleList();
}

