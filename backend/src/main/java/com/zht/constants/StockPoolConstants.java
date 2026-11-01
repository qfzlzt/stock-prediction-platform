package com.zht.constants;

import java.util.Arrays;
import java.util.List;

public final class StockPoolConstants {

    private StockPoolConstants() {
    }

    public static final List<String> DEFAULT_STOCK_CODES = Arrays.asList(
            "688041.SH", "688981.SH", "688256.SH", "688795.SH", "688235.SH", "688802.SH",
            "688012.SH", "688008.SH", "688347.SH", "688111.SH", "688521.SH", "688818.SH",
            "688506.SH", "688072.SH", "688271.SH", "688525.SH", "688783.SH", "688775.SH",
            "688702.SH", "688082.SH", "688223.SH", "688498.SH","688001.SH","688009.SH",
            "688027.SH","688036.SH","688110.SH","688126.SH","688183.SH","688187.SH",
            "688385.SH","688396.SH","688568.SH","688585.SH","688777.SH"
    );

    public static final String DAILY_FIELDS =
            "pe_ttm,pb_mrq,pct_chg,ev,mkt_cap_float,total_shares,share_issuing_mkt,maxup,maxdown,chg,vwap,volume,amt,turn,vol_ratio,high,low,open,close,pre_close,adjfactor";

    public  static final String DAILY_OPTIONS =
            "ruleType=3;unit=1;currencyType=;VolumeRatio_N=5;MTM_interDay=12;MTM_N=6;MTM_IO=1;";

    public static final String TECH_FIELDS =
            "tech_MA20,tech_MA60,tech_revs20,volatilityratio,tech_vr";

    public static final String TECH_OPTIONS =
            "CalculationTime=20;AnnualCoefficient=252;";

    public static final String REALTIME_FIELDS =
            "rt_date,rt_time,rt_latest,rt_chg,rt_pct_chg,rt_vwap,rt_vol,rt_amt,rt_turn,rt_vol_ratio,rt_high,rt_low,rt_open,rt_pre_close,rt_pre_latest,rt_adj_factor";

    public static final String REALTIME_MINUTE_FIELDS =
            "close,chg,pct_chg,vwap,volume,amt,turn,vol_ratio,high,low,open,pre_close,adjfactor";

    public static final String REALTIME_MINUTE_OPTIONS = "BarSize=1";
}
