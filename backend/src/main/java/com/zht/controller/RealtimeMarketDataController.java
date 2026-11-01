// RealtimeMarketDataController.java
package com.zht.controller;

import com.zht.commons.r.R;
import com.zht.entity.RealtimeMarketData;
import com.zht.entity.dto.WindSyncRequest;
import com.zht.service.RealtimeMarketDataService;
import com.zht.service.WindSyncService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.List;

@RestController
@RequestMapping("/api/realtime-market-data")
@CrossOrigin(origins = "*")
public class RealtimeMarketDataController {
    
    @Autowired
    private RealtimeMarketDataService realtimeMarketDataService;

    @Autowired
    private WindSyncService windSyncService;
    
    @GetMapping("/list")
    public R<List<RealtimeMarketData>> queryList(@RequestParam(required = false) String stockCode) {
//        WindSyncRequest request = new WindSyncRequest();
//        request.setSyncDaily(false);
//        request.setSyncRealtime(true);
//        request.setSyncTechnical(false);
//        if (stockCode != null && !stockCode.trim().isEmpty()) {
//            request.setStockCodes(Arrays.asList(stockCode.trim()));
//        }
//        windSyncService.syncMarketData(request);

        List<RealtimeMarketData> list = realtimeMarketDataService.queryList(stockCode);
        return R.succ(list);
    }
    
    @GetMapping("/{id}")
    public R<RealtimeMarketData> getById(@PathVariable Long id) {
        RealtimeMarketData data = realtimeMarketDataService.getById(id);
        return R.succ(data);
    }
    
    @PostMapping
    public R<?> add(@RequestBody RealtimeMarketData data) {
        realtimeMarketDataService.save(data);
        return R.succ(null);
    }
    
    @PutMapping("/{id}")
    public R<?> update(@PathVariable Long id, @RequestBody RealtimeMarketData data) {
        data.setId(id);
        realtimeMarketDataService.updateById(data);
        return R.succ(null);
    }
    
    @DeleteMapping("/{id}")
    public R<?> delete(@PathVariable Long id) {
        realtimeMarketDataService.removeById(id);
        return R.succ(null);
    }
    
    @GetMapping("/export")
    public void export(@RequestParam(required = false) String stockCode) {
        // 导出Excel逻辑
    }
}
