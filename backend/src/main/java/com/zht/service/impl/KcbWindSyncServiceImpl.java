package com.zht.service.impl;

import com.wind.api.W;
import com.wind.api.struct.WindData;
import com.zht.config.WindDllConfig;
import com.zht.dao.KcbCloseDailyDao;
import com.zht.entity.KcbCloseDaily;
import com.zht.service.KcbWindSyncService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

@Service
public class KcbWindSyncServiceImpl implements KcbWindSyncService {

    private static final Logger log = LoggerFactory.getLogger(KcbWindSyncServiceImpl.class);

    private static final String KCB_SECTOR_CODE = "1000033376000000";
    private static final String FIELD_ARITHMETIC = "sec_close_avg";
    private static final String FIELD_TOTAL_WEIGHTED = "sec_close_tswavg";
    private static final String FIELD_FLOAT_WEIGHTED = "sec_close_ffswavg_chn";
    private static final LocalDate DEFAULT_START_DATE = LocalDate.of(2022, 1, 4);
    private static final DateTimeFormatter DATE_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    private final KcbCloseDailyDao kcbCloseDailyDao;
    private final WindDllConfig.WindReadyChecker windReadyChecker;

    public KcbWindSyncServiceImpl(KcbCloseDailyDao kcbCloseDailyDao,
                                  WindDllConfig.WindReadyChecker windReadyChecker) {
        this.kcbCloseDailyDao = kcbCloseDailyDao;
        this.windReadyChecker = windReadyChecker;
    }

    @Override
    public String syncIncremental() {
        windReadyChecker.ensureReady();

        LocalDate today = LocalDate.now();
        Date maxTradeDate = kcbCloseDailyDao.selectMaxTradeDate();
        LocalDate startDate = maxTradeDate == null
                ? DEFAULT_START_DATE
                : toLocalDate(maxTradeDate).plusDays(1);

        if (startDate.isAfter(today)) {
            log.info("[KCB-Wind] 库内最新日期 {}，无需同步", maxTradeDate);
            return "科创板数据已是最新，无需同步";
        }

        String start = startDate.format(DATE_FMT);
        String end = today.format(DATE_FMT);
        log.info("[KCB-Wind] 开始增量同步，区间 {} -> {}", start, end);

        Map<LocalDate, BigDecimal> arithmetic = fetchSeries(FIELD_ARITHMETIC, start, end);
        Map<LocalDate, BigDecimal> totalWeighted = fetchSeries(FIELD_TOTAL_WEIGHTED, start, end);
        Map<LocalDate, BigDecimal> floatWeighted = fetchSeries(FIELD_FLOAT_WEIGHTED, start, end);

        TreeSet<LocalDate> dates = new TreeSet<>();
        dates.addAll(arithmetic.keySet());
        dates.addAll(totalWeighted.keySet());
        dates.addAll(floatWeighted.keySet());

        if (dates.isEmpty()) {
            log.warn("[KCB-Wind] 三个字段都没有返回可写入数据");
            return "Wind 未返回新的科创板区间数据";
        }

        int saved = 0;
        for (LocalDate date : dates) {
            KcbCloseDaily item = new KcbCloseDaily();
            item.setTradeDate(java.sql.Date.valueOf(date));
            item.setCloseArithmetic(arithmetic.get(date));
            item.setCloseTotalWeighted(totalWeighted.get(date));
            item.setCloseFloatWeighted(floatWeighted.get(date));
            item.setStockCount(null);
            kcbCloseDailyDao.upsert(item);
            saved++;
        }

        log.info("[KCB-Wind] 同步完成，共写入/更新 {} 条，日期范围 {} -> {}", saved, dates.first(), dates.last());

        return "Wind 科创板同步完成，范围 " + start + " -> " + end + "，写入/更新 " + saved + " 条";
    }

    private Map<LocalDate, BigDecimal> fetchSeries(String field, String startDate, String endDate) {
        log.info("[KCB-Wind] 调用 wses，field={}, sector={}, start={}, end={}",
                field, KCB_SECTOR_CODE, startDate, endDate);
        WindData windData = W.wses(KCB_SECTOR_CODE, field, startDate, endDate, "");
        if (windData == null) {
            throw new IllegalStateException("Wind 返回为空: " + field);
        }
        if (windData.getErrorId() != 0) {
            throw new IllegalStateException("Wind 调用失败 field=" + field + ", errorId=" + windData.getErrorId());
        }

        List<LocalDate> dates = extractDates(windData.getTimes());
        List<BigDecimal> values = extractDecimals(windData.getData());
        int size = Math.min(dates.size(), values.size());
        Map<LocalDate, BigDecimal> result = new LinkedHashMap<>();
        for (int i = 0; i < size; i++) {
            LocalDate date = dates.get(i);
            BigDecimal value = values.get(i);
            if (date != null && value != null) {
                result.put(date, value.setScale(4, RoundingMode.HALF_UP));
            }
        }
        log.info("[KCB-Wind] field={} 返回 timePoints={}, valuePoints={}, usablePoints={}",
                field, dates.size(), values.size(), result.size());
        return result;
    }

    private List<LocalDate> extractDates(Object raw) {
        List<LocalDate> result = new ArrayList<>();
        if (raw instanceof List) {
            for (Object item : (List<?>) raw) {
                LocalDate date = toLocalDate(item);
                if (date != null) {
                    result.add(date);
                }
            }
            return result;
        }
        if (raw instanceof Object[]) {
            for (Object item : (Object[]) raw) {
                LocalDate date = toLocalDate(item);
                if (date != null) {
                    result.add(date);
                }
            }
        }
        return result;
    }

    private List<BigDecimal> extractDecimals(Object raw) {
        List<BigDecimal> result = new ArrayList<>();
        if (raw instanceof List) {
            for (Object item : (List<?>) raw) {
                appendDecimal(result, item);
            }
            return result;
        }
        if (raw instanceof Object[][]) {
            Object[][] array = (Object[][]) raw;
            for (Object[] row : array) {
                for (Object item : row) {
                    appendDecimal(result, item);
                }
            }
            return result;
        }
        if (raw instanceof Object[]) {
            for (Object item : (Object[]) raw) {
                appendDecimal(result, item);
            }
        } else {
            appendDecimal(result, raw);
        }
        return result;
    }

    private void appendDecimal(List<BigDecimal> target, Object value) {
        if (value == null) {
            return;
        }
        try {
            String text = value.toString().trim();
            if (text.isEmpty() || "null".equalsIgnoreCase(text) || "NaN".equalsIgnoreCase(text)) {
                return;
            }
            target.add(new BigDecimal(text));
        } catch (Exception ignored) {
        }
    }

    private LocalDate toLocalDate(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Date) {
            return Instant.ofEpochMilli(((Date) value).getTime())
                    .atZone(ZoneId.systemDefault())
                    .toLocalDate();
        }
        String text = value.toString().trim();
        if (text.isEmpty()) {
            return null;
        }
        if (text.length() >= 10) {
            text = text.substring(0, 10);
        }
        return LocalDate.parse(text, DATE_FMT);
    }
}
