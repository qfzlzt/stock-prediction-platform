// TechnicalIndicatorLibraryController.java
package com.zht.controller;


import com.zht.commons.r.R;
import com.zht.entity.TechnicalIndicatorLibrary;
import com.zht.entity.dto.TechnicalQuery;
import com.zht.service.TechnicalIndicatorLibraryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/technical-indicators")
@CrossOrigin(origins = "*")
public class TechnicalIndicatorLibraryController {
    
    @Autowired
    private TechnicalIndicatorLibraryService technicalIndicatorLibraryService;
    
    @GetMapping("/list")
    public R<List<TechnicalIndicatorLibrary>> queryList(TechnicalQuery query) {
        List<TechnicalIndicatorLibrary> list = technicalIndicatorLibraryService.queryList(query);
        return R.succ(list);
    }
    
    @GetMapping("/{id}")
    public R<TechnicalIndicatorLibrary> getById(@PathVariable Long id) {
        TechnicalIndicatorLibrary data = technicalIndicatorLibraryService.getById(id);
        return R.succ(data);
    }
    
    @PostMapping
    public R<?> add(@RequestBody TechnicalIndicatorLibrary data) {
        technicalIndicatorLibraryService.save(data);
        return R.succ(null);
    }
    
    @PutMapping("/{id}")
    public R<?> update(@PathVariable Long id, @RequestBody TechnicalIndicatorLibrary data) {
        data.setId(id);
        technicalIndicatorLibraryService.updateById(data);
        return R.succ(null);
    }
    
    @DeleteMapping("/{id}")
    public R<?> delete(@PathVariable Long id) {
        technicalIndicatorLibraryService.removeById(id);
        return R.succ(null);
    }
    
    @GetMapping("/export")
    public void export(TechnicalQuery query) {
        // 导出Excel逻辑
    }
}