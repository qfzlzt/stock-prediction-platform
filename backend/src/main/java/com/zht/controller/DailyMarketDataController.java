// DailyMarketDataController.java
package com.zht.controller;


import com.zht.commons.r.R;
import com.zht.entity.DailyMarketData;
import com.zht.entity.HistoricalDataVO;
import com.zht.entity.dto.DailyQuery;
import com.zht.entity.dto.WindSyncRequest;
import com.zht.service.DailyMarketDataService;
import com.zht.service.WindSyncService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.List;

@RestController
@RequestMapping("/api/daily-market-data")
@CrossOrigin(origins = "*")
public class DailyMarketDataController {
    
    @Autowired
    private DailyMarketDataService dailyMarketDataService;

    @Autowired
    private WindSyncService windSyncService;
    
    @GetMapping("/list")
    public R<List<DailyMarketData>> queryList(DailyQuery query) {
//        WindSyncRequest request = new WindSyncRequest();
//        request.setSyncDaily(true);
//        request.setSyncRealtime(false);
//        request.setSyncTechnical(false);
//        if (query != null && query.getStockCode() != null && !query.getStockCode().trim().isEmpty()) {
//            request.setStockCodes(Arrays.asList(query.getStockCode().trim()));
//        }
//        windSyncService.syncMarketData(request);

        List<DailyMarketData> list = dailyMarketDataService.queryList(query);
        return R.succ(list);
    }
    
    @GetMapping("/{id}")
    public R<DailyMarketData> getById(@PathVariable Long id) {
        DailyMarketData data = dailyMarketDataService.getById(id);
        return R.succ(data);
    }
    @GetMapping("/history")
    public R getHistoricalData(
            @RequestParam String stockCode,
            @RequestParam String metric,
            @RequestParam(defaultValue = "60") Integer days) {

        List<HistoricalDataVO> data = dailyMarketDataService.getHistoricalData(stockCode, metric, days);
        return R.succ(data);
    }
    
    @PostMapping
    public R<?> add(@RequestBody DailyMarketData data) {
        dailyMarketDataService.save(data);
        return R.succ(null);
    }
    
    @PutMapping("/{id}")
    public R<?> update(@PathVariable Long id, @RequestBody DailyMarketData data) {
        data.setId(id);
        dailyMarketDataService.updateById(data);
        return R.succ(null);
    }
    
    @DeleteMapping("/{id}")
    public R<?> delete(@PathVariable Long id) {
        dailyMarketDataService.removeById(id);
        return R.succ(null);
    }
    
    @GetMapping("/export")
    public void export(DailyQuery query) {
        // 导出Excel逻辑
    }
}
