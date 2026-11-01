// CompanyProfileController.java
package com.zht.controller;


import com.baomidou.mybatisplus.core.metadata.IPage;
import com.zht.commons.r.R;
import com.zht.entity.CompanyProfile;
import com.zht.entity.dto.CompanyQuery;
import com.zht.service.CompanyProfileService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/company-profiles")
@CrossOrigin(origins = "*")
public class CompanyProfileController {
    
    @Autowired
    private CompanyProfileService companyProfileService;
    
    @GetMapping("/page")
    public R<IPage<CompanyProfile>> queryPage(CompanyQuery query) {
        IPage<CompanyProfile> page = companyProfileService.queryPage(query);
        return R.succ(page);
    }
    
    @GetMapping("/list")
    public R<List<CompanyProfile>> getSimpleList() {
        List<CompanyProfile> list = companyProfileService.getSimpleList();
        return R.succ(list);
    }
    
    @GetMapping("/{id}")
    public R<CompanyProfile> getById(@PathVariable Long id) {
        CompanyProfile company = companyProfileService.getById(id);
        return R.succ(company);
    }
    
    @PostMapping
    public R<?> add(@RequestBody CompanyProfile company) {
        companyProfileService.save(company);
        return R.succ(null);
    }
    
    @PutMapping("/{id}")
    public R<?> update(@PathVariable Long id, @RequestBody CompanyProfile company) {
        companyProfileService.updateById(company);
        return R.succ(null);
    }
    
    @DeleteMapping("/{id}")
    public R<?> delete(@PathVariable Long id) {
        companyProfileService.removeById(id);
        return R.succ(null);
    }
    
    @GetMapping("/export")
    public void export(CompanyQuery query) {
        // 导出Excel逻辑，可使用EasyExcel
        // 为简化示例，这里省略具体实现
    }
}