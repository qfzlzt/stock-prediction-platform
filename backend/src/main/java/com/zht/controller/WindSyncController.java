package com.zht.controller;

import com.zht.commons.r.R;
import com.zht.entity.dto.WindSyncRequest;
import com.zht.entity.dto.WindSyncResult;
import com.zht.service.WindSyncService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/wind")
@CrossOrigin(origins = "*")
public class WindSyncController {

    private final WindSyncService windSyncService;

    public WindSyncController(WindSyncService windSyncService) {
        this.windSyncService = windSyncService;
    }

    @PostMapping("/sync-market-data")
    public R<WindSyncResult> syncMarketData(@RequestBody(required = false) WindSyncRequest request) {
        if (request == null) {
            request = new WindSyncRequest();
        }
        return R.succ(windSyncService.syncMarketData(request));
    }
}
