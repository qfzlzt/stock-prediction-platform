package com.zht.service;

import com.zht.entity.dto.WindSyncRequest;
import com.zht.entity.dto.WindSyncResult;

public interface WindSyncService {
    WindSyncResult syncMarketData(WindSyncRequest request);


}
