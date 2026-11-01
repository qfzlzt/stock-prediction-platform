package com.zht.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import com.zht.dao.CompanyProfileDao;
import com.zht.entity.CompanyProfile;
import com.zht.entity.dto.CompanyQuery;
import com.zht.service.CompanyProfileService;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.util.List;

/**
 * 公司概况表(CompanyProfile)表服务实现类
 *
 * @author makejava
 * @since 2026-03-08 04:30:47
 */
@Service("companyProfileService")
public class CompanyProfileServiceImpl extends ServiceImpl<CompanyProfileDao, CompanyProfile> implements CompanyProfileService {

    @Override
    public IPage<CompanyProfile> queryPage(CompanyQuery query) {
        Page<CompanyProfile> page = new Page<>(query.getPageNum(), query.getPageSize());
        LambdaQueryWrapper<CompanyProfile> wrapper = new LambdaQueryWrapper<>();

        // 关键词查询（股票代码、名称、行业）
        if (StringUtils.hasText(query.getKeyword())) {
            wrapper.and(w -> w.like(CompanyProfile::getStockcode, query.getKeyword())
                    .or()
                    .like(CompanyProfile::getStockname, query.getKeyword())
                    .or()
                    .like(CompanyProfile::getIndustrylevel, query.getKeyword()));
        }

        // 省份模糊查询 - 只在province有值时添加条件
        if (StringUtils.hasText(query.getProvince())) {
            // 处理省份查询，同时匹配带"市"和不带"市"的情况
            String province = query.getProvince();
            wrapper.and(w -> {
                w.like(CompanyProfile::getRegistrationprovince, province);

                // 如果输入的是"上海"，也匹配"上海市"
                if (!province.contains("市")) {
                    w.or().like(CompanyProfile::getRegistrationprovince, province + "市");
                }
                // 如果输入的是"上海市"，也匹配"上海"
                if (province.contains("市")) {
                    w.or().like(CompanyProfile::getRegistrationprovince, province.replace("市", ""));
                }
            });
        }
        // 如果province为空，不添加任何省份查询条件，保持查询所有记录

        // 状态精确查询
        if (StringUtils.hasText(query.getStatus())) {
            wrapper.eq(CompanyProfile::getStatus, query.getStatus());
        }

        // 排序
        wrapper.orderByAsc(CompanyProfile::getStockcode);

        return this.page(page, wrapper);
    }

    @Override
    public List<CompanyProfile> getSimpleList() {
        return baseMapper.selectSimpleList();
    }
}

