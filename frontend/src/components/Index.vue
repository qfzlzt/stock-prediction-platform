<template>
  <div id="app">
    <div class="app-container">
      <!-- 侧边导航 -->
      <div class="sidebar">
        <div class="logo">
          <div class="logo-text">智股<span>分析</span>系统</div>
        </div>

        <div class="nav-menu">
          <div 
            class="nav-item" 
            :class="{ active: activeNav === 'company' }"
            @click="switchNav('company')"
          >
            <i class="nav-icon">🏢</i>
            <span class="nav-text">公司概况</span>
          </div>
          <div 
            class="nav-item" 
            :class="{ active: activeNav === 'financial' }"
            @click="switchNav('financial')"
          >
            <i class="nav-icon">📊</i>
            <span class="nav-text">财务状况</span>
          </div>
          <div 
            class="nav-item" 
            :class="{ active: activeNav === 'daily' }"
            @click="switchNav('daily')"
          >
            <i class="nav-icon">📈</i>
            <span class="nav-text">日频数据</span>
          </div>
          <div 
            class="nav-item" 
            :class="{ active: activeNav === 'realtime' }"
            @click="switchNav('realtime')"
          >
            <i class="nav-icon">⏰</i>
            <span class="nav-text">实时数据</span>
          </div>
          <div 
            class="nav-item" 
            :class="{ active: activeNav === 'technical' }"
            @click="switchNav('technical')"
          >
            <i class="nav-icon">📐</i>
            <span class="nav-text">技术指标</span>
          </div>
          <div
            class="nav-item"
            :class="{ active: activeNav === 'analysis' }"
            @click="switchNav('analysis')"
          >
            <i class="nav-icon">📝</i>
            <span class="nav-text">分析报告</span>
          </div>
          <div
            class="nav-item"
            @click="$router.push('/kcb-index')"
          >
            <i class="nav-icon">📉</i>
            <span class="nav-text">科创板指数</span>
          </div>
        </div>

        <div class="user-info" @click="goToUserPage">
          <div class="user-avatar">
            <i>👤</i>
          </div>
          <div class="user-details">
            <div class="user-name">{{ username || '管理员' }}</div>
            <div class="user-role">系统管理员</div>
          </div>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="main-content" :class="{ 'with-detail-panel': showDetailPanel }">
        <div class="content-wrapper">
          <div class="header">
            <div class="page-title">{{ pageTitles[activeNav] }}</div>
            <div class="header-actions">
              <el-input 
                class="search-box" 
                :placeholder="getSearchPlaceholder()" 
                v-model="searchKeyword" 
                clearable
                @keyup.enter="handleSearch"
                @clear="handleClearSearch"
              >
                <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
              </el-input>
              <el-button type="primary" icon="el-icon-refresh" @click="refreshData">刷新</el-button>
              <el-button v-if="activeNav !== 'company'" icon="el-icon-download" @click="exportData">导出</el-button>
            </div>
          </div>

          <div class="content-area">
            <div class="content-card">
              <div class="card-header">
                <div class="card-title">{{ pageTitles[activeNav] }}列表</div>
                <div class="card-actions">
                  <el-button v-if="activeNav === 'company'" type="primary" icon="el-icon-plus" @click="showAddDialog = true">添加公司</el-button>
                </div>
              </div>

              <div class="card-body">
                <!-- 加载状态 -->
                <div v-if="loading[activeNav]" class="loading-container">
                  <el-spinner></el-spinner>
                  <div class="loading-text">数据加载中...</div>
                </div>

                <!-- 公司概况内容 -->
                <div v-if="activeNav === 'company'" class="company-content">
                  <div class="filter-bar">
                    <el-input
                      v-model="companyQuery.keyword"
                      placeholder="搜索公司名称、股票代码或行业"
                      style="width: 300px;"
                      @keyup.enter="loadCompanyData"
                    >
                      <el-button slot="append" icon="el-icon-search" @click="loadCompanyData"></el-button>
                    </el-input>
                    <el-select v-model="companyQuery.province" clearable placeholder="选择省份" style="width: 150px; margin-left: 10px;" @change="loadCompanyData">
                      <el-option v-for="province in provinces" :key="province" :label="province" :value="province"></el-option>
                    </el-select>
                    <el-select v-model="companyQuery.status" clearable placeholder="交易状态" style="width: 150px; margin-left: 10px;" @change="loadCompanyData">
                      <el-option label="正常交易" value="L"></el-option>
                      <el-option label="停牌" value="S"></el-option>
                      <el-option label="退市整理期" value="D"></el-option>
                      <el-option label="已退市" value="T"></el-option>
                    </el-select>
                  </div>

                  <el-table
                    ref="companyTable"
                    :data="companyData"
                    row-key="id"
                    stripe
                    max-height="600"
                    style="width: 100%"
                    @row-click="viewCompanyDetail"
                    v-loading="loading.company"
                  >
                    <el-table-column prop="id" label="ID" width="80" v-if="false"></el-table-column>
                    <el-table-column prop="stockcode" label="证券代码" width="120"></el-table-column>
                    <el-table-column prop="stockname" label="证券简称" width="120"></el-table-column>
                    <el-table-column prop="englishname" label="英文简称" width="150" show-overflow-tooltip></el-table-column>
                    <el-table-column prop="markettype" label="上市板" width="100"></el-table-column>
                    <el-table-column prop="stockcategory" label="股票类别" width="100"></el-table-column>
                    <el-table-column prop="listingdate" label="上市日期" width="120">
                      <template slot-scope="scope">{{ formatDate(scope.row.listingdate) }}</template>
                    </el-table-column>
                    <el-table-column prop="status" label="交易状态" width="120">
                      <template slot-scope="scope">
                        <el-tag :type="getStatusTagType(scope.row.status)" size="small">{{ getStatusLabel(scope.row.status) }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="industrylevel" label="所属行业" width="200" show-overflow-tooltip></el-table-column>
                    <el-table-column prop="legalrepresentative" label="法定代表人" width="120"></el-table-column>
                    <el-table-column prop="registeredcapital" label="注册资本(元)" width="150">
                      <template slot-scope="scope">{{ formatNumber(scope.row.registeredcapital) }}</template>
                    </el-table-column>
                    <el-table-column prop="registrationtime" label="成立日期" width="120">
                      <template slot-scope="scope">{{ formatDate(scope.row.registrationtime) }}</template>
                    </el-table-column>
                    <el-table-column prop="registrationprovince" label="省份" width="100"></el-table-column>
                    <el-table-column prop="employeecount" label="员工总数" width="100">
                      <template slot-scope="scope">{{ scope.row.employeecount }}人</template>
                    </el-table-column>
                    <el-table-column prop="independentdirectors" label="独立董事" width="200" show-overflow-tooltip></el-table-column>
                    <el-table-column label="操作" width="150">
                      <template slot-scope="scope">
                        <el-button type="text" size="small" @click.stop="editCompany(scope.row)">编辑</el-button>
                        <el-button type="text" size="small" @click.stop="viewCompanyDetail(scope.row)">详情</el-button>
                        <el-button type="text" size="small" @click.stop="deleteCompany(scope.row)">删除</el-button>
                      </template>
                    </el-table-column>
                  </el-table>

                  <div class="pagination">
                    <el-pagination
                      background
                      layout="total, prev, pager, next, sizes"
                      :total="companyTotal"
                      :page-size="companyQuery.pageSize"
                      :page-sizes="[10, 20, 50, 100]"
                      :current-page="companyQuery.pageNum"
                      @size-change="handleCompanySizeChange"
                      @current-change="handleCompanyPageChange">
                    </el-pagination>
                  </div>
                </div>

                <!-- 财务状况内容 -->
                <div v-if="activeNav === 'financial'" class="financial-content">
                  <div class="filter-bar">
                    <el-select v-model="financialQuery.stockCode" clearable filterable placeholder="选择股票" style="width: 200px;" @change="loadFinancialData">
                      <el-option 
                        v-for="company in companies" 
                        :key="company.stockcode" 
                        :label="`${company.stockname} (${company.stockcode})`" 
                        :value="company.stockcode">
                      </el-option>
                    </el-select>
                    <el-select v-model="financialQuery.reportPeriod" clearable placeholder="报告年份" style="width: 120px; margin-left: 10px;" @change="loadFinancialData">
                      <el-option v-for="year in availableYears" :key="year" :label="year" :value="year"></el-option>
                    </el-select>
                    <el-select v-model="financialQuery.reportType" clearable placeholder="报告类型" style="width: 120px; margin-left: 10px;" @change="loadFinancialData">
                      <el-option label="一季报" value="Q1"></el-option>
                      <el-option label="半年报" value="S1"></el-option>
                      <el-option label="三季报" value="Q3"></el-option>
                      <el-option label="年报" value="A"></el-option>
                    </el-select>
                    <el-button type="primary" icon="el-icon-search" @click="loadFinancialData" style="margin-left: 10px;">查询</el-button>
                    <el-button @click="resetFinancialQuery">重置</el-button>
                  </div>

                  <div class="table-scroll-container" ref="financialTableContainer">
                    <el-table
                      ref="financialTable"
                      :data="financialData"
                      stripe
                      style="width: 100%"
                      v-loading="loading.financial"
                      :key="financialTableKey"
                    >
                      <el-table-column prop="id" label="ID" width="80" v-if="false"></el-table-column>
                      <el-table-column prop="stockcode" label="证券代码" width="120"></el-table-column>
                      <el-table-column prop="stockname" label="公司名称" width="150" show-overflow-tooltip></el-table-column>
                      <el-table-column prop="reportperiod" label="报告年份" width="100"></el-table-column>
                      <el-table-column prop="reporttype" label="报告类型" width="100">
                        <template slot-scope="scope">{{ getReportTypeLabel(scope.row.reporttype) }}</template>
                      </el-table-column>
                      <el-table-column prop="basiceps" label="基本每股收益(元)" width="150">
                        <template slot-scope="scope">{{ formatRatio(scope.row.basiceps) }}</template>
                      </el-table-column>
                      <el-table-column prop="netassetspershare" label="每股净资产(元)" width="150">
                        <template slot-scope="scope">{{ formatRatio(scope.row.netassetspershare) }}</template>
                      </el-table-column>
                      <el-table-column prop="capitalreserve" label="资本公积金(元)" width="150">
                        <template slot-scope="scope">{{ formatNumber(scope.row.capitalreserve) }}</template>
                      </el-table-column>
                      <el-table-column prop="undistributedprofitpershare" label="每股未分配利润(元)" width="150">
                        <template slot-scope="scope">{{ formatRatio(scope.row.undistributedprofitpershare) }}</template>
                      </el-table-column>
                      <el-table-column prop="operatingcashflowpershare" label="每股现金净额(元)" width="150">
                        <template slot-scope="scope">{{ formatRatio(scope.row.operatingcashflowpershare) }}</template>
                      </el-table-column>
                      <el-table-column prop="totaloperatingrevenue" label="营业总收入(元)" width="150">
                        <template slot-scope="scope">{{ formatNumber(scope.row.totaloperatingrevenue) }}</template>
                      </el-table-column>
                      <el-table-column prop="netprofitattributable" label="净利润(元)" width="150">
                        <template slot-scope="scope">{{ formatNumber(scope.row.netprofitattributable) }}</template>
                      </el-table-column>
                      <el-table-column prop="totaloperatingrevenueyoy" label="营收同比" width="120">
                        <template slot-scope="scope">
                          <span :class="scope.row.totaloperatingrevenueyoy >= 0 ? 'positive' : 'negative'">
                            {{ formatPercent(scope.row.totaloperatingrevenueyoy) }}%
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="roe" label="ROE(%)" width="100">
                        <template slot-scope="scope">{{ formatPercent(scope.row.roe) }}</template>
                      </el-table-column>
                      <el-table-column prop="grossmargin" label="毛利率(%)" width="100">
                        <template slot-scope="scope">{{ formatPercent(scope.row.grossmargin) }}</template>
                      </el-table-column>
                      <el-table-column label="财报预览" width="220">
                        <template slot-scope="scope">
                          <el-button 
                            type="primary" 
                            size="mini" 
                            icon="el-icon-view"
                            @click.stop="previewFinancialReport(scope.row)"
                          >预览</el-button>
                          <el-button 
                            type="success" 
                            size="mini" 
                            icon="el-icon-download"
                            @click.stop="downloadFinancialReportPDF(scope.row)"
                          >下载</el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </div>

                <!-- 日频数据内容 -->
                <div v-if="activeNav === 'daily'" class="daily-content">
                  <div class="filter-bar">
                    <el-select v-model="dailyQuery.stockCode" clearable filterable placeholder="选择股票" style="width: 200px;" @change="loadDailyData">
                      <el-option 
                        v-for="company in companies" 
                        :key="company.stockcode" 
                        :label="`${company.stockname} (${company.stockcode})`" 
                        :value="company.stockcode">
                      </el-option>
                    </el-select>
                    <el-date-picker
                      v-model="dailyQuery.dateRange"
                      type="daterange"
                      range-separator="至"
                      start-placeholder="开始日期"
                      end-placeholder="结束日期"
                      value-format="yyyy-MM-dd"
                      style="width: 240px; margin-left: 10px;"
                      @change="loadDailyData">
                    </el-date-picker>
                    <el-button type="primary" icon="el-icon-search" @click="loadDailyData" style="margin-left: 10px;">查询</el-button>
                    <el-button @click="resetDailyQuery">重置</el-button>
                    <el-button type="info" icon="el-icon-sort" @click="clearSort">清除排序</el-button>
                  </div>

                  <div class="table-scroll-container">
                    <el-table
                      ref="dailyTable"
                      :data="sortedDailyData"
                      stripe
                      style="width: 100%"
                      v-loading="loading.daily"
                      @header-click="handleHeaderClick"
                      :default-sort="defaultSort"
                      height="600"
                    >
                      <el-table-column prop="tradeDate" label="交易日期" width="120" sortable="custom">
                        <template slot-scope="scope">{{ formatTradeDate(scope.row.tradeDate) }}</template>
                      </el-table-column>
                      
                      <el-table-column prop="stockCode" label="证券代码" width="120" sortable="custom">
                        <template slot-scope="scope">
                          <span>{{ scope.row.stockCode }}</span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="pe" label="市盈率" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'pe', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatRatio(scope.row.pe) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="pb" label="市净率" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'pb', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatRatio(scope.row.pb) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="pctChg" label="涨跌幅" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            :class="['hoverable-cell', scope.row.pctChg >= 0 ? 'positive' : 'negative']"
                            @mouseenter="showHistoricalChart(scope.row, 'pctChg', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatPercent(scope.row.pctChg) }}%
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="ev" label="总市值(亿元)" width="150" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'ev', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatNumber(scope.row.ev / 100000000) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="mktCapFloat" label="流通市值(亿元)" width="150" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'mktCapFloat', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatNumber(scope.row.mktCapFloat / 100000000) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="totalShares" label="总股本(万股)" width="150" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'totalShares', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatShares(scope.row.totalShares) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="shareIssuingMkt" label="流通股本(万股)" width="150" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'shareIssuingMkt', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatShares(scope.row.shareIssuingMkt) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="chg" label="涨跌" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            :class="['hoverable-cell', scope.row.chg >= 0 ? 'positive' : 'negative']"
                            @mouseenter="showHistoricalChart(scope.row, 'chg', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatPrice(scope.row.chg) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="vwap" label="均价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'vwap', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatPrice(scope.row.vwap) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="volume" label="成交量(手)" width="120" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'volume', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatNumber(scope.row.volume) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="amt" label="成交额(亿元)" width="150" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'amt', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatNumber(scope.row.amt / 100000000) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="turn" label="换手率" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'turn', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatPercent(scope.row.turn) }}%
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="volRatio" label="量比" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'volRatio', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatRatio(scope.row.volRatio) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="high" label="最高价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'high', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatPrice(scope.row.high) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="low" label="最低价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'low', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatPrice(scope.row.low) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="open" label="开盘价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'open', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatPrice(scope.row.open) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="close" label="收盘价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'close', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatPrice(scope.row.close) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="preClose" label="前收盘价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'preClose', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatPrice(scope.row.preClose) }}
                          </span>
                        </template>
                      </el-table-column>
                      
                      <el-table-column prop="adjfactor" label="复权因子" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span 
                            class="hoverable-cell"
                            @mouseenter="showHistoricalChart(scope.row, 'adjfactor', 'daily')"
                            @mouseleave="hideHistoricalChart"
                          >
                            {{ formatRatio(scope.row.adjfactor) }}
                          </span>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </div>

                <!-- 实时数据内容 - 删除了鼠标悬停显示历史走势图功能 -->
                <div v-if="activeNav === 'realtime'" class="realtime-content">
                  <div class="filter-bar">
                    <el-select v-model="realtimeQuery.stockCode" clearable filterable placeholder="选择股票" style="width: 200px;" @change="loadRealtimeData">
                      <el-option 
                        v-for="company in companies" 
                        :key="company.stockcode" 
                        :label="`${company.stockname} (${company.stockcode})`" 
                        :value="company.stockcode">
                      </el-option>
                    </el-select>
                    <el-button type="primary" icon="el-icon-search" @click="loadRealtimeData" style="margin-left: 10px;">查询</el-button>
                    <el-button @click="resetRealtimeQuery">重置</el-button>
                    <el-button type="success" icon="el-icon-refresh" @click="refreshRealtimeData" style="margin-left: 10px;">刷新实时数据</el-button>
                    <el-button type="info" icon="el-icon-sort" @click="clearSort">清除排序</el-button>
                  </div>

                  <div class="table-scroll-container">
                    <el-table
                      :data="sortedRealtimeData"
                      stripe
                      style="width: 100%"
                      v-loading="loading.realtime"
                      @header-click="handleHeaderClick"
                      :default-sort="defaultSort"
                    >
                      <el-table-column prop="stockcode" label="证券代码" width="120"></el-table-column>
                      <el-table-column prop="latestprice" label="最新价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span :class="scope.row.pricechange >= 0 ? 'positive' : 'negative'">
                            ¥{{ formatPrice(scope.row.latestprice) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="pricechange" label="涨跌" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span :class="scope.row.pricechange >= 0 ? 'positive' : 'negative'">
                            {{ scope.row.pricechange >= 0 ? '+' : '' }}{{ formatPrice(scope.row.pricechange) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="pricechangerate" label="涨幅" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span :class="scope.row.pricechangerate >= 0 ? 'positive' : 'negative'">
                            {{ formatPercent(scope.row.pricechangerate) }}%
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="averageprice" label="均价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            ¥{{ formatPrice(scope.row.averageprice) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="totalvolume" label="成交量(手)" width="120" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            {{ formatNumber(scope.row.totalvolume) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="turnover" label="成交额(亿元)" width="150" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            {{ formatNumber(scope.row.turnover) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="turnoverrate" label="换手率" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            {{ formatPercent(scope.row.turnoverrate) }}%
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="volumeratio" label="量比" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            {{ formatRatio(scope.row.volumeratio) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="highestprice" label="最高价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            ¥{{ formatPrice(scope.row.highestprice) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="lowestprice" label="最低价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            ¥{{ formatPrice(scope.row.lowestprice) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="openingprice" label="开盘价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            ¥{{ formatPrice(scope.row.openingprice) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="precloseprice" label="前收盘价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            ¥{{ formatPrice(scope.row.precloseprice) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="closeprice" label="收盘价" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            ¥{{ formatPrice(scope.row.closeprice) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="adjfactor" label="复权因子" width="100" sortable="custom">
                        <template slot-scope="scope">
                          <span>
                            {{ formatRatio(scope.row.adjfactor) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="datatimestamp" label="数据时间" width="180">
                        <template slot-scope="scope">{{ formatDateTime(scope.row.datatimestamp) }}</template>
                      </el-table-column>
                    </el-table>
                  </div>
                </div>

                <!-- 技术指标内容 -->
                <div v-if="activeNav === 'technical'" class="technical-content">
                  <div class="technical-top-tags" v-if="selectedTechnicalIndicators.length">
                    <el-tag
                      v-for="item in selectedTechnicalIndicators"
                      :key="item.value"
                      closable
                      size="mini"
                      class="technical-indicator-tag"
                      @close="removeTechnicalIndicator(item)"
                    >
                      {{ item.label }}
                    </el-tag>
                  </div>

                  <div class="technical-search-bar">
                    <el-autocomplete
                      v-model="technicalSearchKeyword"
                      :fetch-suggestions="queryTechnicalIndicators"
                      :placeholder="currentTechnicalPlaceholder"
                      clearable
                      class="technical-search-input"
                      @select="handleTechnicalIndicatorSelect"
                      @keyup.enter.native="searchTechnicalIndicators"
                    >
                      <template slot-scope="{ item }">
                        <div class="technical-suggestion-item">
                          <span class="technical-suggestion-name">{{ item.label }}</span>
                          <span class="technical-suggestion-key">{{ item.value }}</span>
                        </div>
                      </template>
                    </el-autocomplete>

                    <el-button type="primary" icon="el-icon-search" @click="searchTechnicalIndicators">搜索</el-button>
                    <el-button @click="resetTechnicalQuery">重置</el-button>
                  </div>

                  <div class="table-scroll-container technical-table-container">
                    <el-table
                      :data="technicalData"
                      stripe
                      style="width: 100%"
                      v-loading="loading.technical"
                    >
                      <el-table-column prop="id" label="ID" width="80" v-if="false"></el-table-column>
                      <el-table-column prop="stockcode" label="证券代码" width="120"></el-table-column>
                      <el-table-column prop="tradedate" label="交易日期" width="120">
                        <template slot-scope="scope">{{ formatDate(scope.row.tradedate) }}</template>
                      </el-table-column>
                      <el-table-column
                        v-for="item in displayedTechnicalIndicators"
                        :key="item.value"
                        :prop="item.value"
                        :label="item.label"
                        min-width="140"
                        show-overflow-tooltip
                      >
                        <template slot-scope="scope">
                          <span v-if="item.value === 'momentum20'" :class="scope.row.momentum20 >= 0 ? 'positive' : 'negative'">
                            {{ formatPercent(scope.row.momentum20) }}%
                          </span>
                          <span v-else-if="item.value === 'volatility20'">{{ formatPercent(scope.row.volatility20) }}%</span>
                          <span v-else-if="item.value === 'ma20' || item.value === 'ma60'">{{ formatPrice(scope.row[item.value]) }}</span>
                          <span v-else-if="item.value === 'relativevolume'">{{ formatRatio(scope.row.relativevolume) }}</span>
                          <span v-else-if="item.value === 'calculatedat'">{{ formatDateTime(scope.row.calculatedat) }}</span>
                          <span v-else>{{ scope.row[item.value] || '--' }}</span>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </div>

                <!-- 分析报告内容 -->
                <div v-if="activeNav === 'analysis'" class="analysis-content">
                  <div class="filter-bar">
                    <el-select v-model="analysisQuery.stockCode" clearable filterable placeholder="选择股票" style="width: 200px;" @change="loadAnalysisData">
                      <el-option 
                        v-for="company in companies" 
                        :key="company.stockcode" 
                        :label="`${company.stockname} (${company.stockcode})`" 
                        :value="company.stockcode">
                      </el-option>
                      <el-option label="全部市场" value="ALL"></el-option>
                    </el-select>
                    <el-select v-model="analysisQuery.reportType" clearable placeholder="报告类型" style="width: 150px; margin-left: 10px;" @change="loadAnalysisData">
                      <el-option label="策略回测报告" value="策略回测报告"></el-option>
                      <el-option label="技术分析报告" value="技术分析报告"></el-option>
                      <el-option label="基本面分析报告" value="基本面分析报告"></el-option>
                      <el-option label="风险评估报告" value="风险评估报告"></el-option>
                    </el-select>
                    <el-select v-model="analysisQuery.reportStatus" clearable placeholder="报告状态" style="width: 120px; margin-left: 10px;" @change="loadAnalysisData">
                      <el-option label="草稿" value="草稿"></el-option>
                      <el-option label="已发布" value="已发布"></el-option>
                      <el-option label="已归档" value="已归档"></el-option>
                    </el-select>
                    <el-button type="primary" icon="el-icon-search" @click="loadAnalysisData" style="margin-left: 10px;">查询</el-button>
                    <el-button @click="resetAnalysisQuery">重置</el-button>
                  </div>

                  <div class="table-scroll-container">
                    <el-table
                      :data="analysisData"
                      stripe
                      style="width: 100%"
                      v-loading="loading.analysis"
                    >
                      <el-table-column prop="reportid" label="报告ID" width="150"></el-table-column>
                      <el-table-column prop="stockcode" label="证券代码" width="120"></el-table-column>
                      <el-table-column prop="reporttitle" label="报告标题" width="300" show-overflow-tooltip></el-table-column>
                      <el-table-column prop="reporttype" label="报告类型" width="150"></el-table-column>
                      <el-table-column prop="reportabstract" label="报告摘要" width="300" show-overflow-tooltip></el-table-column>
                      <el-table-column prop="reportauthor" label="报告作者" width="150"></el-table-column>
                      <el-table-column prop="reportgeneratetime" label="生成时间" width="180">
                        <template slot-scope="scope">{{ formatDateTime(scope.row.reportgeneratetime) }}</template>
                      </el-table-column>
                      <el-table-column prop="reportstatus" label="报告状态" width="120">
                        <template slot-scope="scope">
                          <el-tag :type="getReportStatusTagType(scope.row.reportstatus)" size="small">{{ scope.row.reportstatus }}</el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column label="操作" width="220" fixed="right">
                        <template slot-scope="scope">
                          <el-button type="primary" size="mini" icon="el-icon-view" @click.stop="previewAnalysisReport(scope.row)">预览</el-button>
                          <el-button type="success" size="mini" icon="el-icon-download" @click.stop="downloadAnalysisReportPDF(scope.row)">下载</el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧详情面板 -->
        <div class="detail-panel" v-if="showDetailPanel" :class="{ 'fullscreen': detailPanelFullscreen }">
          <div class="detail-panel-header">
            <div class="detail-panel-title">{{ detailPanelTitle }}</div>
            <div class="detail-panel-actions">
              <el-button type="text" icon="el-icon-full-screen" @click="toggleDetailPanelFullscreen"></el-button>
              <el-button type="text" icon="el-icon-close" @click="closeDetailPanel"></el-button>
            </div>
          </div>
          <div class="detail-panel-content">
            <!-- 历史数据图表 -->
            <div v-if="detailPanelType === 'chart'" class="chart-container">
              <div class="chart-info">
                <div class="stock-info">{{ detailPanelData.stockName }} ({{ detailPanelData.stockCode }})</div>
                <div class="metric-info">{{ getMetricLabel(detailPanelData.metric) }} - 历史走势 (最近60天)</div>
              </div>
              <div id="historicalChart" style="width: 100%; height: 400px;"></div>
            </div>
            
            <!-- PDF 数据预览 -->
            <div v-if="detailPanelType === 'financialReport' || detailPanelType === 'analysisReport'" class="financial-report-container">
              <div class="report-header">
                <div>
                  <h2>{{ detailPanelData.companyName }} {{ detailPanelData.panelLabel || '报告' }} PDF</h2>
                  <div class="report-period">{{ getDetailPanelSubtitle() }}</div>
                </div>
                <div class="pdf-status-tag" v-if="currentLocalPdf && currentLocalPdf.fileName">
                  当前文件：{{ currentLocalPdf.fileName }}
                </div>
              </div>

              <div class="pdf-toolbar">
                <el-select
                  v-model="selectedPdfKey"
                  placeholder="请选择PDF文件"
                  style="width: 360px"
                  @change="handlePdfSelectionChange"
                >
                  <el-option
                    v-for="item in currentPdfOptions"
                    :key="item.id"
                    :label="item.fileName"
                    :value="item.id"
                  ></el-option>
                </el-select>
                <el-button
                  type="primary"
                  icon="el-icon-refresh"
                  @click="loadPdfManifest(true)"
                >
                  刷新PDF清单
                </el-button>
                <el-button
                  type="success"
                  icon="el-icon-download"
                  :disabled="!currentLocalPdf || !currentLocalPdf.url"
                  @click="downloadCurrentDisplayedPdf"
                >
                  下载当前PDF
                </el-button>
              </div>

              <div class="report-content">
                <div class="info-section">
                  <h3>PDF 文件信息</h3>
                  <table class="info-table">
                    <tr>
                      <td>证券代码</td>
                      <td>{{ detailPanelData.stockCode }}</td>
                      <td>公司名称</td>
                      <td>{{ detailPanelData.companyName }}</td>
                    </tr>
                    <tr>
                      <td>报告年份</td>
                      <td>{{ detailPanelData.reportPeriod || '-' }}</td>
                      <td>报告类型</td>
                      <td>{{ getDisplayReportType(detailPanelData.reportType, detailPanelType) }}</td>
                    </tr>
                  </table>
                </div>

                <div class="pdf-preview-container">
                  <iframe
                    v-if="currentLocalPdf && currentLocalPdf.url"
                    :src="currentLocalPdf.url + '#toolbar=1&navpanes=0&scrollbar=1'"
                    class="pdf-preview-frame"
                    frameborder="0"
                  ></iframe>
                  <div v-else class="pdf-empty-state">
                    <i class="el-icon-document"></i>
                    <div>当前没有可预览的本地PDF文件</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <el-dialog
        :title="(pdfDialogMode === 'preview' || pdfDialogMode === 'analysis-preview') ? '选择要预览的PDF文件' : '选择要下载的PDF文件'"
        :visible.sync="showPdfDialog"
        width="600px"
      >
        <div class="pdf-select-dialog">
          <div class="pdf-select-tip">
            财务状况会读取 <code>public/pdfs/pdf-manifest.json</code>，分析报告会读取 <code>public/pdfs/companyfile/pdf-manifest.json</code>，并按公司简称(stockname) 自动匹配。
          </div>
          <el-radio-group v-model="selectedPdfKey" class="pdf-radio-group">
            <el-radio
              v-for="item in currentPdfOptions"
              :key="item.id"
              :label="item.id"
              class="pdf-radio-item"
            >
              {{ item.fileName }}
            </el-radio>
          </el-radio-group>
          <el-empty v-if="!currentPdfOptions.length" description="没有匹配到可用的PDF文件"></el-empty>
        </div>
        <span slot="footer">
          <el-button @click="showPdfDialog = false">取消</el-button>
          <el-button
            type="primary"
            :disabled="!selectedPdfKey"
            @click="confirmPdfSelection"
          >
            {{ (pdfDialogMode === 'preview' || pdfDialogMode === 'analysis-preview') ? '确认预览' : '确认下载' }}
          </el-button>
        </span>
      </el-dialog>

      <!-- 添加/编辑公司对话框 -->
      <el-dialog 
        :title="dialogTitle" 
        :visible.sync="showAddDialog" 
        width="60%" 
        @close="resetCompanyForm"
      >
        <el-form :model="companyForm" label-width="120px" ref="companyForm">
          <el-input v-model="companyForm.id" type="hidden" v-if="false"></el-input>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="证券代码" prop="stockcode" required>
                <el-input v-model="companyForm.stockcode"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="证券简称" prop="stockname" required>
                <el-input v-model="companyForm.stockname"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="英文简称" prop="englishname">
                <el-input v-model="companyForm.englishname"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="上市版" prop="markettype">
                <el-select v-model="companyForm.markettype" style="width: 100%">
                  <el-option label="主板" value="主板"></el-option>
                  <el-option label="科创板" value="科创板"></el-option>
                  <el-option label="创业板" value="创业板"></el-option>
                  <el-option label="北交所" value="北交所"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="股票类别" prop="stockcategory">
                <el-select v-model="companyForm.stockcategory" style="width: 100%">
                  <el-option label="A股" value="A股"></el-option>
                  <el-option label="B股" value="B股"></el-option>
                  <el-option label="优先股" value="优先股"></el-option>
                  <el-option label="存托凭证" value="存托凭证"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="上市日期" prop="listingdate">
                <el-date-picker v-model="companyForm.listingdate" type="date" style="width: 100%"></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="交易状态" prop="status">
                <el-select v-model="companyForm.status" style="width: 100%">
                  <el-option label="正常交易" value="L"></el-option>
                  <el-option label="停牌" value="S"></el-option>
                  <el-option label="退市整理期" value="D"></el-option>
                  <el-option label="已退市" value="T"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属行业" prop="industrylevel">
                <el-input v-model="companyForm.industrylevel"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="法定代表人" prop="legalrepresentative">
                <el-input v-model="companyForm.legalrepresentative"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="注册资本" prop="registeredcapital">
                <el-input-number v-model="companyForm.registeredcapital" :precision="2" style="width: 100%"></el-input-number>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="成立日期" prop="registrationtime">
                <el-date-picker v-model="companyForm.registrationtime" type="date" style="width: 100%"></el-date-picker>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="省份" prop="registrationprovince">
                <el-input v-model="companyForm.registrationprovince"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="员工总数" prop="employeecount">
                <el-input-number v-model="companyForm.employeecount" :min="0" style="width: 100%"></el-input-number>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="独立董事" prop="independentdirectors">
                <el-input v-model="companyForm.independentdirectors"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="24">
              <el-form-item label="公司简介" prop="companyintro">
                <el-input type="textarea" :rows="3" v-model="companyForm.companyintro"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="24">
              <el-form-item label="经营范围" prop="businessscope">
                <el-input type="textarea" :rows="3" v-model="companyForm.businessscope"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        <span slot="footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="saveCompany">{{ isEdit ? '保存修改' : '确定添加' }}</el-button>
        </span>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  components: {},
  data() {
    return {
      activeNav: 'company',
      username: localStorage.getItem('username') || '管理员',
      searchKeyword: '',
      pageTitles: {
        company: '公司概况',
        financial: '财务状况',
        daily: '日频数据',
        realtime: '实时数据',
        technical: '技术指标',
        analysis: '分析报告'
      },

      companyData: [],
      companyTotal: 0,
      companyQuery: {
        pageNum: 1,
        pageSize: 10,
        keyword: '',
        province: '',
        status: ''
      },

      financialData: [],
      financialQuery: {
        stockCode: '',
        reportPeriod: '',
        reportType: ''
      },

      dailyData: [],
      dailyQuery: {
        stockCode: '',
        dateRange: [],
        sortBy: '',
        sortOrder: ''
      },

      realtimeData: [],
      realtimeQuery: {
        stockCode: ''
      },

      technicalData: [],
      technicalQuery: {
        stockCode: '',
        tradeDate: ''
      },
      technicalSearchKeyword: '',
      technicalPlaceholderIndex: 0,
      technicalPlaceholderTimer: null,
      technicalIndicatorOptions: [
        { label: 'MA5', value: 'ma5' },
        { label: 'MA10', value: 'ma10' },
        { label: 'MA20', value: 'ma20' },
        { label: 'MA60', value: 'ma60' },
        { label: 'RSI6', value: 'rsi6' },
        { label: 'RSI14', value: 'rsi14' },
        { label: 'MACD', value: 'macd' },
        { label: 'MACD信号线', value: 'macdSignal' },
        { label: 'MACD柱值', value: 'macdHist' },
        { label: 'BOLL中轨', value: 'bollMid' },
        { label: 'BOLL上轨', value: 'bollUpper' },
        { label: 'BOLL下轨', value: 'bollLower' },
        { label: 'ATR14', value: 'atr14' },
        { label: '波动率20日', value: 'volatility20' },
        { label: '20日动量', value: 'momentum20' },
        { label: '量比', value: 'volRatio' },
        { label: '换手率', value: 'turn' },
        { label: '成交量均线5日', value: 'volumeMa5' },
        { label: '成交量均线20日', value: 'volumeMa20' },
        { label: '价格动量20日', value: 'priceMomentum20d' }
      ],
      selectedTechnicalIndicators: [],
      searchedTechnicalIndicators: [],

      analysisData: [],
      analysisQuery: {
        stockCode: '',
        reportType: '',
        reportStatus: ''
      },

      companies: [],
      provinces: [
        '北京', '上海', '天津', '重庆',
        '广东省', '江苏省', '浙江省', '安徽省', '福建省', '江西省',
        '山东省', '河南省', '湖北省', '湖南省', '四川省', '贵州省',
        '云南省', '陕西省', '甘肃省', '青海省', '辽宁省', '吉林省',
        '黑龙江省', '海南省', '台湾省', '内蒙古', '广西', '西藏',
        '宁夏', '新疆', '香港', '澳门'
      ],
      availableYears: [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018],

      loading: {
        company: false,
        financial: false,
        daily: false,
        realtime: false,
        technical: false,
        analysis: false
      },

      showAddDialog: false,
      isEdit: false,
      dialogTitle: '添加公司',
      companyForm: {
        id: null,
        stockcode: '',
        stockname: '',
        englishname: '',
        markettype: '科创板',
        stockcategory: 'A股',
        listingdate: '',
        status: 'L',
        industrylevel: '',
        legalrepresentative: '',
        registeredcapital: null,
        registrationtime: '',
        registrationprovince: '',
        employeecount: null,
        independentdirectors: '',
        companyintro: '',
        businessscope: ''
      },

      showDetailPanel: false,
      detailPanelFullscreen: false,
      detailPanelType: '',
      detailPanelTitle: '',
      detailPanelData: {},

      defaultSort: {},
      currentSort: {
        field: '',
        order: ''
      },
      sortableColumns: [
        'tradeDate', 'stockCode', 'pe', 'pb', 'pctChg', 'ev', 'mktCapFloat',
        'totalShares', 'shareIssuingMkt', 'chg', 'vwap', 'volume',
        'amt', 'turn', 'volRatio', 'high', 'low', 'open', 'close',
        'preClose', 'adjfactor',
        'latestprice', 'pricechange', 'pricechangerate', 'averageprice',
        'totalvolume', 'turnover', 'turnoverrate', 'volumeratio',
        'highestprice', 'lowestprice', 'openingprice', 'precloseprice',
        'closeprice'
      ],

      chartInstance: null,
      financialChartInstance: null,
      chartData: [],
      hoverTimer: null,

      showPdfDialog: false,
      pdfDialogMode: 'preview',
      selectedPdfKey: '',
      pendingPdfRow: null,
      currentPdfOptions: [],
      currentLocalPdf: null,
      pdfManifest: [],
      pdfManifestLoaded: false,
      pdfManifestLoading: false,
      
      financialTableKey: 0,
      layoutTimer: null,
      
      analysisPdfManifest: [],
      analysisPdfManifestLoaded: false,
      analysisPdfManifestLoading: false,
      
      // 数据同步相关变量
      nextDayTimer: null,
      lastSyncDate: null
    }
  },

  created() {
    const urlParams = new URLSearchParams(window.location.search);
    const stockCode = urlParams.get('stockCode');
    if (stockCode) {
      this.searchKeyword = stockCode;
      this.handleSearch();
    }
    this.loadPdfManifest();
    this.loadAnalysisPdfManifest();
    // 初始化数据同步
    this.initDataSync();
  },

  mounted() {
    this.loadCompanyData();
    this.loadCompanies();
    this.loadFinancialData();
    this.loadDailyData();
    this.loadRealtimeData();
    this.loadTechnicalData();
    this.loadAnalysisData();
    this.startTechnicalPlaceholderRotation();
    
    window.addEventListener('resize', this.handleWindowResize);
  },

  beforeDestroy() {
    if (this.layoutTimer) {
      clearTimeout(this.layoutTimer);
    }
    if (this.nextDayTimer) {
      clearTimeout(this.nextDayTimer);
    }
    if (this.technicalPlaceholderTimer) {
      clearInterval(this.technicalPlaceholderTimer);
    }
    window.removeEventListener('resize', this.handleWindowResize);
  },

  computed: {
    currentTechnicalPlaceholder() {
      const placeholders = [
        '请输入技术指标，如 20日均线、60日均线、20日动量',
        '可搜索：20日波动率、相对成交量、预测结果',
        '支持多选指标，选中后会在上方显示标签'
      ];
      return placeholders[this.technicalPlaceholderIndex] || placeholders[0];
    },

    displayedTechnicalIndicators() {
      return this.searchedTechnicalIndicators.length
        ? this.searchedTechnicalIndicators
        : this.technicalIndicatorOptions.slice(0, 3);
    },

    sortedDailyData() {
      if (!this.dailyData || this.dailyData.length === 0) return [];
      
      let dataToSort = [...this.dailyData];
      
      if (!this.currentSort.field || !this.currentSort.order) return dataToSort;

      return dataToSort.sort((a, b) => {
        let valA = a[this.currentSort.field];
        let valB = b[this.currentSort.field];

        if (valA === null || valA === undefined) valA = this.currentSort.order === 'asc' ? Infinity : -Infinity;
        if (valB === null || valB === undefined) valB = this.currentSort.order === 'asc' ? Infinity : -Infinity;

        if (this.currentSort.order === 'asc') {
          return valA > valB ? 1 : -1;
        } else {
          return valA < valB ? 1 : -1;
        }
      });
    },

    sortedRealtimeData() {
      if (!this.realtimeData || this.realtimeData.length === 0) return [];
      if (!this.currentSort.field || !this.currentSort.order) return this.realtimeData;

      return [...this.realtimeData].sort((a, b) => {
        let valA = a[this.currentSort.field];
        let valB = b[this.currentSort.field];

        if (valA === null || valA === undefined) valA = -Infinity;
        if (valB === null || valB === undefined) valB = -Infinity;

        if (this.currentSort.order === 'asc') {
          return valA > valB ? 1 : -1;
        } else {
          return valA < valB ? 1 : -1;
        }
      });
    }
  },

  methods: {
    /**
     * 初始化数据同步功能
     */
    initDataSync() {
      // 记录程序启动日期
      const startDate = this.getTodayDateString();
      console.log('程序启动日期:', startDate);
      
      // 立即执行第一次数据同步
      this.syncMarketData();
      
      // 设置到下一个0点的定时器
      this.scheduleNextDaySync();
    },
    
    /**
     * 计算并设置到下一个0点的定时器
     */
    scheduleNextDaySync() {
      const now = new Date();
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(0, 0, 0, 0);
      
      const msUntilMidnight = tomorrow.getTime() - now.getTime();
      
      if (this.nextDayTimer) {
        clearTimeout(this.nextDayTimer);
      }
      
      this.nextDayTimer = setTimeout(() => {
        console.log('检测到跨入第二天，执行数据同步');
        this.syncMarketData();
        // 同步完成后，继续设置下一个0点的定时器
        this.scheduleNextDaySync();
      }, msUntilMidnight);
      
      console.log(`距离下次0点还有 ${Math.floor(msUntilMidnight / 1000 / 60)} 分钟`);
    },
    
    /**
     * 获取当前日期字符串（YYYY-MM-DD格式）
     */
    getTodayDateString() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    /**
     * 调用后端同步接口
     */
    async syncMarketData() {
      const currentDate = this.getTodayDateString();
      console.log('开始同步市场数据...', new Date().toLocaleString(), '当前日期:', currentDate);
      
      try {
        // 调用 POST 接口
        const response = await this.axios.post('http://localhost:9090/api/wind/sync-market-data', {});
        
        if (response.data && response.data.code === 200) {
          this.lastSyncDate = currentDate;
          const msg = response.data.msg || response.data.message || '同步成功';
          console.log('市场数据同步成功:', msg);
          this.$message.success('市场数据同步成功');
          
          // 同步成功后，刷新相关数据
          this.refreshDataAfterSync();
        } else {
          const errorMsg = response.data && response.data.msg ? response.data.msg : '未知错误';
          console.warn('市场数据同步失败:', errorMsg);
          // 同步失败时不更新 lastSyncDate，以便下次继续尝试
        }
      } catch (error) {
        console.error('市场数据同步请求失败:', error);
        this.$message.warning('市场数据同步失败，请检查网络连接');
      }
    },
    
    /**
     * 同步成功后刷新数据
     */
    refreshDataAfterSync() {
      // 刷新当前页面显示的数据
      switch (this.activeNav) {
        case 'daily':
          this.loadDailyData();
          break;
        case 'realtime':
          this.loadRealtimeData();
          break;
        case 'financial':
          this.loadFinancialData();
          break;
        case 'technical':
          this.loadTechnicalData();
          break;
        case 'company':
          this.loadCompanyData();
          break;
        case 'analysis':
          this.loadAnalysisData();
          break;
      }
      
      // 同时刷新公司列表（可能影响下拉选择框）
      this.loadCompanies();
      
      console.log('同步后数据已刷新');
    },
    
    handleWindowResize() {
      if (this.activeNav === 'financial') {
        this.forceFinancialTableLayout();
      }
    },

    forceCompanyTableLayout() {
      this.$nextTick(() => {
        if (this.$refs.companyTable) {
          this.$refs.companyTable.doLayout();
        }
      });
    },

    forceFinancialTableLayout() {
      if (this.layoutTimer) {
        clearTimeout(this.layoutTimer);
      }

      this.$nextTick(() => {
        const table = this.$refs.financialTable;
        const container = this.$refs.financialTableContainer;
        
        if (table) {
          if (typeof table.doLayout === 'function') {
            table.doLayout();
          }
          
          if (table.$el) {
            const tableWrapper = table.$el.querySelector('.el-table__body-wrapper');
            const tableHeader = table.$el.querySelector('.el-table__header-wrapper');
            
            if (tableWrapper) {
              const originalHeight = tableWrapper.style.height;
              tableWrapper.style.height = 'auto';
              if (tableHeader) {
                tableHeader.style.width = 'auto';
              }
              
              this.layoutTimer = setTimeout(() => {
                tableWrapper.style.height = originalHeight || '';
                if (typeof table.doLayout === 'function') {
                  table.doLayout();
                }
                
                setTimeout(() => {
                  if (this.$refs.financialTable && typeof this.$refs.financialTable.doLayout === 'function') {
                    this.$refs.financialTable.doLayout();
                  }
                }, 50);
              }, 30);
            }
          }
        }
        
        if (container) {
          const oldHeight = container.style.maxHeight;
          container.style.maxHeight = 'none';
          setTimeout(() => {
            container.style.maxHeight = oldHeight || '';
          }, 10);
        }
      });
    },

    forceRefreshFinancialTable() {
      this.financialTableKey++;
      this.$nextTick(() => {
        this.forceFinancialTableLayout();
      });
    },

    startTechnicalPlaceholderRotation() {
      if (this.technicalPlaceholderTimer) {
        clearInterval(this.technicalPlaceholderTimer);
      }
      this.technicalPlaceholderTimer = setInterval(() => {
        this.technicalPlaceholderIndex = (this.technicalPlaceholderIndex + 1) % 3;
      }, 2500);
    },

    queryTechnicalIndicators(queryString, cb) {
      const keyword = String(queryString || '').trim().toLowerCase();
      const results = keyword
        ? this.technicalIndicatorOptions.filter(item =>
            item.label.toLowerCase().includes(keyword) || item.value.toLowerCase().includes(keyword)
          )
        : this.technicalIndicatorOptions;
      cb(results);
    },

    handleTechnicalIndicatorSelect(item) {
      const exists = this.selectedTechnicalIndicators.some(selected => selected.value === item.value);
      if (!exists) {
        this.selectedTechnicalIndicators.push(item);
      }
      this.technicalSearchKeyword = '';
    },

    removeTechnicalIndicator(item) {
      this.selectedTechnicalIndicators = this.selectedTechnicalIndicators.filter(selected => selected.value !== item.value);
      this.searchedTechnicalIndicators = this.searchedTechnicalIndicators.filter(selected => selected.value !== item.value);
    },

    searchTechnicalIndicators() {
      if (!this.selectedTechnicalIndicators.length) {
        this.$message.warning('请先选择至少一个技术指标');
        return;
      }
      this.searchedTechnicalIndicators = [...this.selectedTechnicalIndicators];
      this.loadTechnicalData();
    },

    goToUserPage() {
      this.$router.push("/user");
    },

    loadCompanies() {
      this.axios.get('http://localhost:9090/api/company-profiles/list')
        .then(response => {
          const r = response.data;
          if (r.code === 200) {
            this.companies = r.data;
          }
        })
        .catch(error => {
          console.error('加载公司列表失败:', error);
        });
    },

    loadCompanyData() {
      this.loading.company = true;
      this.axios.get('http://localhost:9090/api/company-profiles/page', {
        params: this.companyQuery
      })
      .then(response => {
        const r = response.data;
        if (r.code === 200) {
          this.companyData = Array.isArray(r.data.records) ? r.data.records : [];
          this.companyTotal = r.data.total || 0;
          this.forceCompanyTableLayout();
        } else {
          this.$message.error(r.msg || '加载公司数据失败');
        }
      })
      .catch(error => {
        console.error('加载公司数据失败:', error);
        this.$message.error('网络错误，加载公司数据失败');
      })
      .finally(() => {
        this.loading.company = false;
        this.forceCompanyTableLayout();
      });
    },

    loadFinancialData() {
      this.loading.financial = true;

      this.axios.get('http://localhost:9090/api/financial-reports/list', {
        params: this.financialQuery
      })
      .then(response => {
        const r = response.data;
        if (r.code === 200) {
          this.financialData = Array.isArray(r.data) ? r.data : [];
          this.$nextTick(() => {
            this.forceRefreshFinancialTable();
          });
        } else {
          this.financialData = [];
          this.$nextTick(() => {
            this.forceRefreshFinancialTable();
          });
        }
      })
      .catch(error => {
        console.error('加载财务数据失败:', error);
        this.financialData = [];
        this.$nextTick(() => {
          this.forceRefreshFinancialTable();
        });
      })
      .finally(() => {
        this.loading.financial = false;
      });
    },

    loadDailyData() {
      this.loading.daily = true;
      const params = {
        stockCode: this.dailyQuery.stockCode,
        sortBy: this.dailyQuery.sortBy || this.currentSort.field,
        sortOrder: this.dailyQuery.sortOrder || this.currentSort.order
      };
      if (this.dailyQuery.dateRange && this.dailyQuery.dateRange.length === 2) {
        params.startDate = this.dailyQuery.dateRange[0];
        params.endDate = this.dailyQuery.dateRange[1];
      }

      this.axios.get('http://localhost:9090/api/daily-market-data/list', { params })
        .then(response => {
          const r = response.data;
          if (r.code === 200) {
            this.dailyData = r.data;
            console.log('日频数据加载成功，共', this.dailyData.length, '条');
          } else {
            this.$message.error(r.msg || '加载日频数据失败');
          }
        })
        .catch(error => {
          console.error('加载日频数据失败:', error);
          this.$message.error('网络错误，加载日频数据失败');
        })
        .finally(() => {
          this.loading.daily = false;
          // 强制刷新表格
          this.$nextTick(() => {
            if (this.$refs.dailyTable) {
              this.$refs.dailyTable.doLayout();
            }
          });
        });
    },

    loadRealtimeData() {
      this.loading.realtime = true;
      const params = {
        stockCode: this.realtimeQuery.stockCode,
        sortBy: this.currentSort.field,
        sortOrder: this.currentSort.order
      };

      this.axios.get('http://localhost:9090/api/realtime-market-data/list', { params })
        .then(response => {
          const r = response.data;
          if (r.code === 200) {
            this.realtimeData = r.data;
          } else {
            this.$message.error(r.msg || '加载实时数据失败');
          }
        })
        .catch(error => {
          console.error('加载实时数据失败:', error);
          this.$message.error('网络错误，加载实时数据失败');
        })
        .finally(() => {
          this.loading.realtime = false;
        });
    },

    loadTechnicalData() {
      this.loading.technical = true;
      this.axios.get('http://localhost:9090/api/technical-indicators/list', {
        params: this.technicalQuery
      })
      .then(response => {
        const r = response.data;
        if (r.code === 200) {
          this.technicalData = r.data;
        } else {
          this.$message.error(r.msg || '加载技术指标数据失败');
        }
      })
      .catch(error => {
        console.error('加载技术指标数据失败:', error);
        this.$message.error('网络错误，加载技术指标数据失败');
      })
      .finally(() => {
        this.loading.technical = false;
      });
    },

    loadAnalysisData() {
      this.loading.analysis = true;
      this.axios.get('http://localhost:9090/api/analysis-reports/list', {
        params: this.analysisQuery
      })
      .then(response => {
        const r = response.data;
        if (r.code === 200) {
          this.analysisData = r.data;
        } else {
          this.$message.error(r.msg || '加载分析报告数据失败');
        }
      })
      .catch(error => {
        console.error('加载分析报告数据失败:', error);
        this.$message.error('网络错误，加载分析报告数据失败');
      })
      .finally(() => {
        this.loading.analysis = false;
      });
    },

    refreshRealtimeData() {
      this.loadRealtimeData();
      this.$message.success('实时数据已刷新');
    },

    getSearchPlaceholder() {
      const placeholders = {
        company: '搜索公司名称、股票代码、行业...',
        financial: '搜索股票代码...',
        daily: '搜索股票代码...',
        realtime: '搜索股票代码...',
        technical: '搜索股票代码...',
        analysis: '搜索报告标题、股票代码...'
      };
      return placeholders[this.activeNav] || '搜索...';
    },

    handleSearch() {
      if (!this.searchKeyword.trim()) {
        return;
      }

      switch (this.activeNav) {
        case 'company':
          this.companyQuery.keyword = this.searchKeyword;
          this.companyQuery.pageNum = 1;
          this.loadCompanyData();
          break;
        case 'financial':
          this.financialQuery.stockCode = this.searchKeyword;
          this.loadFinancialData();
          break;
        case 'daily':
          this.dailyQuery.stockCode = this.searchKeyword;
          this.loadDailyData();
          break;
        case 'realtime':
          this.realtimeQuery.stockCode = this.searchKeyword;
          this.loadRealtimeData();
          break;
        case 'technical':
          this.technicalQuery.stockCode = this.searchKeyword;
          this.loadTechnicalData();
          break;
        case 'analysis':
          this.analysisQuery.stockCode = this.searchKeyword;
          this.loadAnalysisData();
          break;
      }
    },

    handleClearSearch() {
      this.searchKeyword = '';
      this.refreshData();
    },

    switchNav(nav) {
      this.activeNav = nav;
      this.searchKeyword = '';
      this.closeDetailPanel();
      this.clearSort();

      switch (nav) {
        case 'company':
          this.companyQuery.keyword = this.searchKeyword;
          this.companyQuery.pageNum = 1;
          this.loadCompanyData();
          break;
        case 'financial':
          this.loadFinancialData();
          this.$nextTick(() => {
            this.forceFinancialTableLayout();
            setTimeout(() => {
              this.forceFinancialTableLayout();
            }, 100);
            setTimeout(() => {
              this.forceFinancialTableLayout();
              if (this.$refs.financialTable) {
                const table = this.$refs.financialTable;
                if (table.$el) {
                  const bodyWrapper = table.$el.querySelector('.el-table__body-wrapper');
                  if (bodyWrapper) {
                    bodyWrapper.style.height = 'auto';
                    setTimeout(() => {
                      bodyWrapper.style.height = '';
                      table.doLayout();
                    }, 10);
                  }
                }
              }
            }, 300);
          });
          break;
        case 'daily':
          this.loadDailyData();
          break;
        case 'realtime':
          this.loadRealtimeData();
          break;
        case 'technical':
          this.loadTechnicalData();
          break;
        case 'analysis':
          this.loadAnalysisData();
          break;
      }

      this.forceCompanyTableLayout();
    },

    refreshData() {
      switch (this.activeNav) {
        case 'company':
          this.companyQuery.keyword = this.searchKeyword;
          this.companyQuery.pageNum = 1;
          this.loadCompanyData();
          break;
        case 'financial':
          this.loadFinancialData();
          break;
        case 'daily':
          this.loadDailyData();
          break;
        case 'realtime':
          this.loadRealtimeData();
          break;
        case 'technical':
          this.loadTechnicalData();
          break;
        case 'analysis':
          this.loadAnalysisData();
          break;
      }
      this.$message.success('数据已刷新');
      this.forceCompanyTableLayout();
      this.forceFinancialTableLayout();
    },

    viewCompanyDetail(row) {
      this.$router.push({
        path: '/companydetail',
        query: {
          id: row.id
        }
      });
    },

    editCompany(row) {
      this.companyForm = JSON.parse(JSON.stringify(row));
      this.isEdit = true;
      this.dialogTitle = '编辑公司';
      this.showAddDialog = true;
    },

    deleteCompany(row) {
      this.$confirm(`确定删除公司 ${row.stockname} (${row.stockcode}) 吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.axios.delete(`http://localhost:9090/api/company-profiles/${row.id}`)
          .then(response => {
            const r = response.data;
            if (r.code === 200) {
              this.$message.success('删除成功');
              this.loadCompanyData();
            } else {
              this.$message.error(r.msg || '删除失败');
            }
          })
          .catch(error => {
            console.error('删除失败:', error);
            this.$message.error('删除失败');
          });
      }).catch(() => {});
    },

    saveCompany() {
      this.$refs.companyForm.validate(valid => {
        if (valid) {
          if (this.isEdit) {
            this.axios.put(`http://localhost:9090/api/company-profiles/${this.companyForm.id}`, this.companyForm)
              .then(response => {
                const r = response.data;
                if (r.code === 200) {
                  this.$message.success('修改成功');
                  this.showAddDialog = false;
                  this.loadCompanyData();
                  this.resetCompanyForm();
                } else {
                  this.$message.error(r.msg || '修改失败');
                }
              })
              .catch(error => {
                console.error('修改失败:', error);
                if (error.response && error.response.data) {
                  this.$message.error(error.response.data.msg || '修改失败');
                } else {
                  this.$message.error('网络错误，修改失败');
                }
              });
          } else {
            this.axios.post('http://localhost:9090/api/company-profiles', this.companyForm)
              .then(response => {
                const r = response.data;
                if (r.code === 200) {
                  this.$message.success('添加成功');
                  this.showAddDialog = false;
                  this.loadCompanyData();
                  this.resetCompanyForm();
                } else {
                  this.$message.error(r.msg || '添加失败');
                }
              })
              .catch(error => {
                console.error('添加失败:', error);
                this.$message.error('添加失败');
              });
          }
        }
      });
    },

    resetCompanyForm() {
      this.companyForm = {
        id: null,
        stockcode: '',
        stockname: '',
        englishname: '',
        markettype: '科创板',
        stockcategory: 'A股',
        listingdate: '',
        status: 'L',
        industrylevel: '',
        legalrepresentative: '',
        registeredcapital: null,
        registrationtime: '',
        registrationprovince: '',
        employeecount: null,
        independentdirectors: '',
        companyintro: '',
        businessscope: ''
      };
      this.isEdit = false;
      this.dialogTitle = '添加公司';

      if (this.$refs.companyForm) {
        this.$refs.companyForm.clearValidate();
      }
    },

    resetFinancialQuery() {
      this.financialQuery = {
        stockCode: '',
        reportPeriod: '',
        reportType: ''
      };
      this.loadFinancialData();
    },

    resetDailyQuery() {
      this.dailyQuery = {
        stockCode: '',
        dateRange: [],
        sortBy: '',
        sortOrder: ''
      };
      this.loadDailyData();
    },

    resetRealtimeQuery() {
      this.realtimeQuery = { stockCode: '' };
      this.loadRealtimeData();
    },

    resetTechnicalQuery() {
      this.technicalQuery = { stockCode: '', tradeDate: '' };
      this.technicalSearchKeyword = '';
      this.selectedTechnicalIndicators = [];
      this.searchedTechnicalIndicators = [];
      this.loadTechnicalData();
    },

    resetAnalysisQuery() {
      this.analysisQuery = { stockCode: '', reportType: '', reportStatus: '' };
      this.loadAnalysisData();
    },

    viewReportDetail(row) {
      this.previewAnalysisReport(row);
    },

    downloadReport(row) {
      this.downloadAnalysisReportPDF(row);
    },

    getDetailPanelSubtitle() {
      if (this.detailPanelType === 'analysisReport') {
        return this.detailPanelData.reportType || '分析报告';
      }
      if (this.detailPanelData.reportPeriod && this.detailPanelData.reportType) {
        return `${this.detailPanelData.reportPeriod}年 ${this.getReportTypeLabel(this.detailPanelData.reportType)}`;
      }
      return '';
    },

    getDisplayReportType(reportType, panelType) {
      if (panelType === 'analysisReport') {
        return reportType || '-';
      }
      return this.getReportTypeLabel(reportType);
    },

    getAnalysisTypeKeywords(reportType) {
      const type = String(reportType || '').trim();
      const mapping = {
        '策略回测报告': ['策略回测报告', '策略回测', '回测报告', '回测'],
        '技术分析报告': ['技术分析报告', '技术分析'],
        '基本面分析报告': ['基本面分析报告', '基本面分析', '基本面'],
        '风险评估报告': ['风险评估报告', '风险评估', '风险']
      };
      return mapping[type] || (type ? [type] : []);
    },

    getAvailableAnalysisPdfFiles(row) {
      const stockName = this.getRowStockName(row);
      const normalizedStockName = this.normalizePdfMatchText(stockName);
      const reportTypeKeywords = this.getAnalysisTypeKeywords(row.reporttype)
        .map(keyword => this.normalizePdfMatchText(keyword))
        .filter(Boolean);
      const reportTitle = this.normalizePdfMatchText(row.reporttitle || '');

      return this.analysisPdfManifest.filter(item => {
        const itemStockName = this.normalizePdfMatchText(item.stockName);
        if (itemStockName !== normalizedStockName) return false;

        const fileNameText = this.normalizePdfMatchText(item.fileName || '');
        const titleMatched = reportTitle && fileNameText.includes(reportTitle);
        const typeMatched = !reportTypeKeywords.length || reportTypeKeywords.some(keyword => fileNameText.includes(keyword));
        return titleMatched || typeMatched;
      });
    },

    async previewAnalysisReport(row, selectedFile = null) {
      const ready = await this.ensureAnalysisPdfManifest();
      if (!ready) return;

      if (this.detailPanelType === 'chart') {
        this.closeDetailPanel();
      }

      const stockName = this.getRowStockName(row);
      const pdfOptions = this.getAvailableAnalysisPdfFiles(row);

      if (!pdfOptions.length) {
        this.$message.warning(`没有找到 ${stockName} ${row.reporttype || '分析报告'} 对应的 PDF 文件`);
        return;
      }

      const activeFile = selectedFile || pdfOptions[0];

      this.detailPanelType = 'analysisReport';
      this.detailPanelTitle = `${stockName} ${row.reporttype || '分析报告'} PDF预览`;
      this.detailPanelData = {
        ...row,
        companyName: stockName,
        stockCode: row.stockcode,
        reportPeriod: row.reportperiod || '',
        reportType: row.reporttype || '',
        panelLabel: '分析报告'
      };
      this.currentPdfOptions = pdfOptions;
      this.currentLocalPdf = activeFile;
      this.selectedPdfKey = activeFile ? activeFile.id : '';
      this.showDetailPanel = true;
    },

    async downloadAnalysisReportPDF(row) {
      const ready = await this.ensureAnalysisPdfManifest();
      if (!ready) return;

      const pdfOptions = this.getAvailableAnalysisPdfFiles(row);

      if (!pdfOptions.length) {
        this.$message.warning(`没有找到 ${this.getRowStockName(row)} ${row.reporttype || '分析报告'} 对应的 PDF 文件`);
        return;
      }

      if (pdfOptions.length === 1) {
        this.downloadLocalPdf(pdfOptions[0]);
        return;
      }

      this.pendingPdfRow = row;
      this.pdfDialogMode = 'analysis-download';
      this.currentPdfOptions = pdfOptions;
      this.selectedPdfKey = pdfOptions[0].id;
      this.showPdfDialog = true;
    },

    downloadCurrentDisplayedPdf() {
      if (!this.currentLocalPdf) {
        this.$message.warning('没有正在预览的PDF文件');
        return;
      }
      this.downloadLocalPdf(this.currentLocalPdf);
    },

    exportData() {
      let url = '';
      let params = {};

      switch (this.activeNav) {
        case 'company':
          url = 'http://localhost:9090/api/company-profiles/export';
          params = this.companyQuery;
          break;
        case 'financial':
          url = 'http://localhost:9090/api/financial-reports/export';
          params = this.financialQuery;
          break;
        case 'daily':
          url = 'http://localhost:9090/api/daily-market-data/export';
          params = { ...this.dailyQuery };
          if (params.dateRange && params.dateRange.length === 2) {
            params.startDate = params.dateRange[0];
            params.endDate = params.dateRange[1];
            delete params.dateRange;
          }
          break;
        case 'realtime':
          url = 'http://localhost:9090/api/realtime-market-data/export';
          params = this.realtimeQuery;
          break;
        case 'technical':
          url = 'http://localhost:9090/api/technical-indicators/export';
          params = this.technicalQuery;
          break;
        case 'analysis':
          url = 'http://localhost:9090/api/analysis-reports/export';
          params = this.analysisQuery;
          break;
      }

      const queryString = Object.keys(params)
        .filter(key => params[key])
        .map(key => `${key}=${encodeURIComponent(params[key])}`)
        .join('&');

      if (queryString) {
        url += '?' + queryString;
      }

      window.open(url, '_blank');
    },

    handleCompanySizeChange(size) {
      this.companyQuery.pageSize = size;
      this.companyQuery.pageNum = 1;
      this.loadCompanyData();
    },

    handleCompanyPageChange(page) {
      this.companyQuery.pageNum = page;
      this.loadCompanyData();
    },

    handleHeaderClick(column) {
      if (!column.sortable) return;

      const field = column.property;
      if (!this.sortableColumns.includes(field)) return;

      let order = 'asc';

      if (this.currentSort.field === field) {
        if (this.currentSort.order === 'asc') {
          order = 'desc';
        } else if (this.currentSort.order === 'desc') {
          order = '';
        }
      }

      this.applySort(field, order);
    },

    applySort(field, order) {
      if (order === '') {
        this.currentSort = { field: '', order: '' };
        this.defaultSort = {};

        if (this.activeNav === 'daily') {
          this.dailyQuery.sortBy = '';
          this.dailyQuery.sortOrder = '';
        }
      } else {
        this.currentSort = { field, order };
        this.defaultSort = { prop: field, order: order };

        if (this.activeNav === 'daily') {
          this.dailyQuery.sortBy = field;
          this.dailyQuery.sortOrder = order;
        }
      }

      if (order === 'asc') {
        this.$message.success(`已按升序排列`);
      } else if (order === 'desc') {
        this.$message.success(`已按降序排列`);
      } else {
        this.$message.info('已清除排序');
      }
    },

    clearSort() {
      this.currentSort = { field: '', order: '' };
      this.defaultSort = {};

      if (this.activeNav === 'daily') {
        this.dailyQuery.sortBy = '';
        this.dailyQuery.sortOrder = '';
      }
    },

    async loadPdfManifest(forceRefresh = false) {
      if (this.pdfManifestLoading) return;
      if (this.pdfManifestLoaded && !forceRefresh) return;

      this.pdfManifestLoading = true;
      try {
        const suffix = forceRefresh ? `?t=${Date.now()}` : '';
        const response = await fetch(`/pdfs/pdf-manifest.json${suffix}`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const manifest = await response.json();
        this.pdfManifest = Array.isArray(manifest) ? manifest.map(item => ({
          ...item,
          url: this.resolvePdfUrl(item.relativePath || item.url || '')
        })) : [];
        this.pdfManifestLoaded = true;

        if (forceRefresh) {
          this.$message.success('PDF 清单已刷新');
        }
      } catch (error) {
        console.error('加载 PDF 清单失败:', error);
        this.pdfManifest = [];
        this.pdfManifestLoaded = false;
        this.$message.warning('未读取到 public/pdfs/pdf-manifest.json，请先执行清单生成脚本');
      } finally {
        this.pdfManifestLoading = false;
      }
    },

    async loadAnalysisPdfManifest(forceRefresh = false) {
      if (this.analysisPdfManifestLoading) return;
      if (this.analysisPdfManifestLoaded && !forceRefresh) return;

      this.analysisPdfManifestLoading = true;
      try {
        const suffix = forceRefresh ? `?t=${Date.now()}` : '';
        const response = await fetch(`/pdfs/companyfile/pdf-manifest.json${suffix}`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const manifest = await response.json();
        this.analysisPdfManifest = Array.isArray(manifest) ? manifest.map(item => ({
          ...item,
          url: this.resolvePdfUrl(item.relativePath || item.url || '')
        })) : [];
        this.analysisPdfManifestLoaded = true;

        if (forceRefresh) {
          this.$message.success('分析报告 PDF 清单已刷新');
        }
      } catch (error) {
        console.error('加载分析报告 PDF 清单失败:', error);
        this.analysisPdfManifest = [];
        this.analysisPdfManifestLoaded = false;
        this.$message.warning('未读取到 public/pdfs/companyfile/pdf-manifest.json，请先执行清单生成脚本');
      } finally {
        this.analysisPdfManifestLoading = false;
      }
    },

    resolvePdfUrl(relativePath) {
      if (!relativePath) return '';
      if (/^https?:\/\//.test(relativePath)) return relativePath;
      const normalizedPath = relativePath.replace(/^\/+/, '');
      const base = process.env.BASE_URL || '/';
      return `${base}${normalizedPath}`;
    },

    normalizePdfMatchText(value) {
      return String(value || '')
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '')
        .replace(/[（）()《》【】\[\]_.-]/g, '');
    },

    getRowStockName(row) {
      const company = this.companies.find(c => c.stockcode === row.stockcode);
      return row.stockname || (company ? company.stockname : '') || row.stockcode || '';
    },

    getFinancialTypeKeywords(reportType) {
      const type = String(reportType || '').trim().toUpperCase();
      const mapping = {
        Q1: ['一季报', '第一季度', '1季报', 'q1'],
        S1: ['半年报', '中报', '半年度', '半年', '6个月', 's1'],
        Q3: ['三季报', '第三季度', '3季报', 'q3'],
        A: ['年报', '年度报告', '年度', '全年', 'a']
      };
      return mapping[type] || [];
    },

    getAvailablePdfFiles(row) {
      const stockName = this.getRowStockName(row);
      const reportPeriod = String(row.reportperiod || row.reportPeriod || '');
      const reportType = String(row.reporttype || row.reportType || '').toUpperCase();
      const normalizedStockName = this.normalizePdfMatchText(stockName);
      const typeKeywords = this.getFinancialTypeKeywords(reportType)
        .map(keyword => this.normalizePdfMatchText(keyword))
        .filter(Boolean);
      const allTypeKeywords = {
        Q1: this.getFinancialTypeKeywords('Q1').map(keyword => this.normalizePdfMatchText(keyword)),
        S1: this.getFinancialTypeKeywords('S1').map(keyword => this.normalizePdfMatchText(keyword)),
        Q3: this.getFinancialTypeKeywords('Q3').map(keyword => this.normalizePdfMatchText(keyword)),
        A: this.getFinancialTypeKeywords('A').map(keyword => this.normalizePdfMatchText(keyword))
      };

      return this.pdfManifest.filter(item => {
        const itemStockName = this.normalizePdfMatchText(item.stockName);
        if (itemStockName !== normalizedStockName) return false;

        const itemPeriod = String(item.reportPeriod || item.year || '');
        if (itemPeriod !== reportPeriod) return false;

        const manifestTypeText = String(item.reportType || '');
        const manifestType = manifestTypeText.toUpperCase();
        const fileNameText = this.normalizePdfMatchText(item.fileName || item.relativePath || item.url || '');

        const exactManifestMatched =
          manifestType === reportType ||
          (reportType === 'S1' && /半年度报告|半年报|中报/.test(manifestTypeText)) ||
          (reportType === 'Q1' && /第一季度报告|一季报/.test(manifestTypeText)) ||
          (reportType === 'Q3' && /第三季度报告|三季报/.test(manifestTypeText)) ||
          (reportType === 'A' && /年报|年度报告/.test(manifestTypeText));

        const fileNameMatched =
          typeKeywords.length > 0 &&
          typeKeywords.some(keyword => fileNameText.includes(keyword));

        if (reportType === 'S1') {
          const looksLikeAnnual = allTypeKeywords.A.some(keyword => fileNameText.includes(keyword));
          return exactManifestMatched || (fileNameMatched && !looksLikeAnnual);
        }

        if (reportType === 'A') {
          const looksLikeHalfYear = allTypeKeywords.S1.some(keyword => fileNameText.includes(keyword));
          return (exactManifestMatched || fileNameMatched) && !looksLikeHalfYear;
        }

        return exactManifestMatched || fileNameMatched;
      });
    },

    async ensurePdfManifest() {
      if (!this.pdfManifestLoaded) {
        await this.loadPdfManifest();
      }
      return this.pdfManifestLoaded;
    },

    async ensureAnalysisPdfManifest() {
      if (!this.analysisPdfManifestLoaded) {
        await this.loadAnalysisPdfManifest();
      }
      return this.analysisPdfManifestLoaded;
    },

    async openPdfSelector(row, mode) {
      const ready = await this.ensurePdfManifest();
      if (!ready) return;

      const pdfOptions = this.getAvailablePdfFiles(row);

      if (!pdfOptions.length) {
        this.$message.warning(`没有找到 ${this.getRowStockName(row)} ${row.reportperiod}年${this.getReportTypeLabel(row.reporttype)} 对应的 PDF 文件`);
        return;
      }

      this.pendingPdfRow = row;
      this.pdfDialogMode = mode;
      this.currentPdfOptions = pdfOptions;
      this.selectedPdfKey = pdfOptions[0].id;
      this.showPdfDialog = true;
    },

    confirmPdfSelection() {
      const file = this.currentPdfOptions.find(item => item.id === this.selectedPdfKey);

      if (!file) {
        this.$message.warning('请先选择PDF文件');
        return;
      }

      this.showPdfDialog = false;

      if (this.pdfDialogMode === 'preview') {
        this.previewFinancialReport(this.pendingPdfRow, file);
      } else if (this.pdfDialogMode === 'analysis-preview') {
        this.previewAnalysisReport(this.pendingPdfRow, file);
      } else {
        this.downloadLocalPdf(file);
      }
    },

    handlePdfSelectionChange(value) {
      const file = this.currentPdfOptions.find(item => item.id === value);
      if (!file) return;

      if (this.detailPanelType === 'financialReport' || this.detailPanelType === 'analysisReport') {
        this.currentLocalPdf = file;
      }
    },

    downloadLocalPdf(file) {
      if (!file || !file.url) {
        this.$message.error('PDF文件地址无效');
        return;
      }

      const link = document.createElement('a');
      link.href = file.url;
      link.download = file.fileName || 'report.pdf';
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      this.$message.success('已开始下载PDF');
    },

    async previewFinancialReport(row, selectedFile = null) {
      const ready = await this.ensurePdfManifest();
      if (!ready) return;

      if (this.detailPanelType === 'chart') {
        this.closeDetailPanel();
      }

      const stockName = this.getRowStockName(row);
      const pdfOptions = this.getAvailablePdfFiles(row);

      if (!pdfOptions.length) {
        this.$message.warning(`没有找到 ${stockName} ${row.reportperiod}年${this.getReportTypeLabel(row.reporttype)} 对应的 PDF 文件`);
        return;
      }

      const activeFile = selectedFile || pdfOptions[0];

      this.detailPanelType = 'financialReport';
      this.detailPanelTitle = `${stockName} ${row.reportperiod}年${this.getReportTypeLabel(row.reporttype)} PDF预览`;
      this.detailPanelData = {
        ...row,
        companyName: stockName,
        stockCode: row.stockcode,
        reportPeriod: row.reportperiod,
        reportType: row.reporttype
      };
      this.currentPdfOptions = pdfOptions;
      this.currentLocalPdf = activeFile;
      this.selectedPdfKey = activeFile ? activeFile.id : '';
      this.showDetailPanel = true;

      this.$nextTick(() => {
        this.forceCompanyTableLayout();
      });
    },

    async downloadFinancialReportPDF(row) {
      const ready = await this.ensurePdfManifest();
      if (!ready) return;

      const pdfOptions = this.getAvailablePdfFiles(row);

      if (!pdfOptions.length) {
        this.$message.warning(`没有找到 ${this.getRowStockName(row)} ${row.reportperiod}年${this.getReportTypeLabel(row.reporttype)} 对应的 PDF 文件`);
        return;
      }

      if (pdfOptions.length === 1) {
        this.downloadLocalPdf(pdfOptions[0]);
        return;
      }

      this.openPdfSelector(row, 'download');
    },

    /**
     * 显示历史走势图 - 仅用于日频数据
     */
    /**
 * 显示历史走势图 - 仅用于日频数据
 */
  showHistoricalChart(row, metric, dataType) {
    console.log('showHistoricalChart 被调用:', { row, metric, dataType });
    
    // 仅处理日频数据的历史图表
    if (dataType !== 'daily') {
      console.log('非日频数据，跳过');
      return;
    }
    
    if (this.hoverTimer) {
      clearTimeout(this.hoverTimer);
    }

    this.hoverTimer = setTimeout(() => {
      // 根据实体类，日频数据的股票代码字段是 stockCode（大写C）
      const stockCode = row.stockCode;
      
      if (!stockCode) {
        console.error('无法获取股票代码，row对象:', row);
        this.$message.error('无法获取股票代码，请检查数据格式');
        return;
      }
      
      // 从 companies 中获取公司名称（注意 companies 中的字段是 stockcode 小写）
      const company = this.companies.find(c => c.stockcode === stockCode);
      const stockName = company ? company.stockname : (row.stockname || stockCode);

      console.log('显示历史走势图:', { stockCode, metric, stockName });

      this.detailPanelType = 'chart';
      this.detailPanelTitle = `${stockName} - ${this.getMetricLabel(metric)} 历史走势`;
      this.detailPanelData = {
        stockCode: stockCode,
        stockName: stockName,
        metric: metric,
        dataType: dataType,
        currentValue: row[metric]
      };

      // 直接调用后端API获取60天历史数据
      this.loadHistoricalDataFromAPI(stockCode, metric, 60);
      this.showDetailPanel = true;

      this.$nextTick(() => {
        this.forceCompanyTableLayout();
      });
    }, 300);
  },

    hideHistoricalChart() {
      if (this.hoverTimer) {
        clearTimeout(this.hoverTimer);
        this.hoverTimer = null;
      }
    },

    /**
     * 从后端API加载历史数据
     * @param {string} stockCode 股票代码
     * @param {string} metric 指标名称
     * @param {number} days 天数，默认60天
     */
    loadHistoricalDataFromAPI(stockCode, metric, days = 60) {
      this.axios.get('http://localhost:9090/api/daily-market-data/history', {
        params: {
          stockCode: stockCode,
          metric: metric,
          days: days
        }
      })
      .then(response => {
        const r = response.data;
        if (r.code === 200 && r.data && r.data.length > 0) {
          this.chartData = r.data;
          this.$nextTick(() => {
            this.renderChart(metric);
          });
        } else {
          console.warn('未获取到历史数据');
          this.chartData = [];
          this.$nextTick(() => {
            this.renderChart(metric);
          });
        }
      })
      .catch(error => {
        console.error('加载历史数据失败:', error);
        this.chartData = [];
        this.$nextTick(() => {
          this.renderChart(metric);
        });
        this.$message.warning('加载历史数据失败');
      });
    },

    renderChart(metric) {
      const chartDom = document.getElementById('historicalChart');
      if (!chartDom) return;

      if (!this.chartInstance) {
        this.chartInstance = echarts.init(chartDom);
      }

      // 从后端返回的数据格式：每个对象包含 date 和 value 字段
      const dates = this.chartData.map(item => {
        if (item.date) {
          return this.formatTradeDate(item.date);
        }
        return item.tradeDate || item.datatimestamp || '';
      });
      const values = this.chartData.map(item => item.value || item[metric] || 0);

      const option = {
        title: {
          text: `${this.detailPanelData.stockName} - ${this.getMetricLabel(metric)}`,
          left: 'center',
          top: 0,
          textStyle: {
            fontSize: 14,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            const data = params[0];
            return `${data.name}<br/>${data.seriesName}: ${data.value ? Number(data.value).toFixed(2) : '--'}`;
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            rotate: 45,
            interval: Math.floor(dates.length / 10)
          }
        },
        yAxis: {
          type: 'value',
          name: this.getMetricLabel(metric),
          nameTextStyle: {
            fontSize: 12
          }
        },
        series: [
          {
            name: this.getMetricLabel(metric),
            type: 'line',
            data: values,
            smooth: true,
            lineStyle: {
              width: 2,
              color: '#409EFF'
            },
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.1)'
            },
            symbol: 'circle',
            symbolSize: 4
          }
        ],
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            start: 0,
            end: 100
          }
        ]
      };

      this.chartInstance.setOption(option);
      
      // 添加窗口大小变化时的自适应
      const resizeHandler = () => {
        if (this.chartInstance) {
          this.chartInstance.resize();
        }
      };
      window.removeEventListener('resize', this.chartResizeHandler);
      this.chartResizeHandler = resizeHandler;
      window.addEventListener('resize', this.chartResizeHandler);
    },

    closeDetailPanel() {
      this.showDetailPanel = false;
      this.detailPanelType = '';
      this.detailPanelTitle = '';
      this.detailPanelData = {};
      this.chartData = [];

      if (this.chartInstance) {
        this.chartInstance.dispose();
        this.chartInstance = null;
      }

      if (this.financialChartInstance) {
        this.financialChartInstance.dispose();
        this.financialChartInstance = null;
      }
      
      // 移除 resize 事件监听
      if (this.chartResizeHandler) {
        window.removeEventListener('resize', this.chartResizeHandler);
        this.chartResizeHandler = null;
      }

      this.forceCompanyTableLayout();
    },

    toggleDetailPanelFullscreen() {
      this.detailPanelFullscreen = !this.detailPanelFullscreen;

      if (this.detailPanelType === 'chart' && this.chartInstance) {
        setTimeout(() => {
          this.chartInstance.resize();
        }, 100);
      }

      if (this.detailPanelType === 'financialReport' && this.financialChartInstance) {
        setTimeout(() => {
          this.financialChartInstance.resize();
        }, 100);
      }

      this.forceCompanyTableLayout();
    },

    getMetricLabel(metric) {
      const metricMap = {
        'pe': '市盈率',
        'pb': '市净率',
        'pctChg': '涨跌幅',
        'ev': '总市值',
        'mktCapFloat': '流通市值',
        'totalShares': '总股本',
        'shareIssuingMkt': '流通股本',
        'chg': '涨跌',
        'vwap': '均价',
        'volume': '成交量',
        'amt': '成交额',
        'turn': '换手率',
        'volRatio': '量比',
        'high': '最高价',
        'low': '最低价',
        'open': '开盘价',
        'close': '收盘价',
        'preClose': '前收盘价',
        'adjfactor': '复权因子',
        'latestprice': '最新价',
        'pricechange': '涨跌',
        'pricechangerate': '涨幅',
        'averageprice': '均价',
        'totalvolume': '成交量',
        'turnover': '成交额',
        'turnoverrate': '换手率',
        'volumeratio': '量比',
        'highestprice': '最高价',
        'lowestprice': '最低价',
        'openingprice': '开盘价',
        'precloseprice': '前收盘价',
        'closeprice': '收盘价'
      };
      return metricMap[metric] || metric;
    },

    formatDate(dateString) {
      if (!dateString) return '--';
      if (typeof dateString === 'string' && dateString.length >= 10) {
        return dateString.slice(0, 10);
      }
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '--';
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      } catch (error) {
        return '--';
      }
    },

    formatTradeDate(dateString) {
      if (!dateString) return '--';
      
      try {
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
          return dateString;
        }
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '--';
        
        const beijingTime = new Date(date.getTime() + 8 * 60 * 60 * 1000);
        
        const year = beijingTime.getUTCFullYear();
        const month = String(beijingTime.getUTCMonth() + 1).padStart(2, '0');
        const day = String(beijingTime.getUTCDate()).padStart(2, '0');
        
        return `${year}-${month}-${day}`;
      } catch (error) {
        console.error('日期格式化错误:', error);
        return '--';
      }
    },

    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '--';
      try {
        const date = new Date(dateTimeString);
        if (isNaN(date.getTime())) return dateTimeString;
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      } catch (error) {
        return dateTimeString;
      }
    },

    formatNumber(num) {
      if (num === null || num === undefined || isNaN(num)) return '--';
      if (Math.abs(num) >= 100000000) {
        return (num / 100000000).toFixed(2) + '亿';
      } else if (Math.abs(num) >= 10000) {
        return (num / 10000).toFixed(2) + '万';
      }
      return Number(num).toFixed(2);
    },

    formatRatio(value) {
      if (value === null || value === undefined || isNaN(value)) return '--';
      return Number(value).toFixed(2);
    },

    formatPercent(value) {
      if (value === null || value === undefined || isNaN(value)) return '--';
      return Number(value).toFixed(2);
    },

    formatPrice(value) {
      if (value === null || value === undefined || isNaN(value)) return '--';
      return Number(value).toFixed(2);
    },

    formatShares(value) {
      if (value === null || value === undefined || isNaN(value)) return '--';
      return (Number(value) / 10000).toFixed(2);
    },

    getReportTypeLabel(type) {
      const map = {
        'Q1': '一季报',
        'S1': '半年报',
        'Q3': '三季报',
        'A': '年报'
      };
      return map[type] || type;
    },

    getStatusLabel(status) {
      const map = {
        'L': '正常交易',
        'S': '停牌',
        'D': '退市整理期',
        'T': '已退市'
      };
      return map[status] || status;
    },

    getStatusTagType(status) {
      const map = {
        'L': 'success',
        'S': 'warning',
        'D': 'danger',
        'T': 'info'
      };
      return map[status] || 'info';
    },

    getReportStatusTagType(status) {
      const map = {
        '已发布': 'success',
        '草稿': 'info',
        '已归档': 'default'
      };
      return map[status] || 'info';
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

body {
  background-color: #f5f7fa;
  color: #333;
  line-height: 1.6;
  height: 100vh;
  overflow: hidden;
}

.app-container {
  margin-top: -60px;
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 260px;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
}

.logo-text span {
  color: #4dabf7;
}

.nav-menu {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  padding: 14px 25px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  border-left: 4px solid transparent;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.15);
  border-left-color: #4dabf7;
}

.nav-icon {
  margin-right: 12px;
  font-size: 18px;
  width: 20px;
  text-align: center;
}

.nav-text {
  font-size: 15px;
  font-weight: 500;
}

.user-info {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.user-role {
  font-size: 12px;
  opacity: 0.8;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  transition: all 0.3s;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-content.with-detail-panel .content-wrapper {
  width: calc(100% - 400px);
}

.header {
  height: 60px;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 25px;
  z-index: 5;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e3c72;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.search-box {
  width: 350px;
}

.content-area {
  flex: 1;
  padding: 25px;
  overflow-y: auto;
  overflow-x: hidden;
  height: calc(100vh - 110px);
}

.content-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 18px 25px;
  background: #f9fafc;
  border-bottom: 1px solid #e6e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.card-actions {
  display: flex;
  gap: 10px;
}

.card-body {
  padding: 25px;
}

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.technical-top-tags {
  margin-bottom: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.technical-indicator-tag {
  margin-right: 0;
}

.technical-search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.technical-search-input {
  width: 420px;
}

.technical-suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.technical-suggestion-name {
  color: #303133;
}

.technical-suggestion-key {
  color: #909399;
  font-size: 12px;
}

.technical-table-container {
  margin-bottom: 0;
}

.table-scroll-container {
  max-height: 600px;
  overflow-y: auto;
  overflow-x: auto;
  border: 1px solid #e6e8f0;
  border-radius: 4px;
  margin-bottom: 20px;
  background: white;
}

.table-scroll-container ::v-deep .el-table {
  border: none;
}

.hoverable-cell {
  cursor: pointer;
  transition: background-color 0.2s;
  padding: 2px 4px;
  border-radius: 2px;
  display: inline-block;
}

.hoverable-cell:hover {
  background-color: #ecf5ff;
}

.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.loading-text {
  margin-top: 10px;
  color: #666;
  font-size: 16px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.positive {
  color: #f56c6c;
  font-weight: 600;
}

.negative {
  color: #67c23a;
  font-weight: 600;
}

.detail-panel {
  width: 400px;
  background: white;
  border-left: 1px solid #e6e8f0;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 20;
  transition: all 0.3s;
  overflow: hidden;
}

.detail-panel.fullscreen {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 80%;
  max-width: 1200px;
  z-index: 1000;
}

.detail-panel-header {
  height: 50px;
  padding: 0 15px;
  background: #f9fafc;
  border-bottom: 1px solid #e6e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e3c72;
}

.detail-panel-actions {
  display: flex;
  gap: 10px;
}

.detail-panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chart-container {
  height: 100%;
  padding: 20px;
}

.chart-info {
  margin-bottom: 20px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.stock-info {
  font-size: 18px;
  font-weight: 600;
  color: #1e3c72;
}

.metric-info {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

#historicalChart {
  width: 100%;
  height: 400px;
}

.financial-report-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  overflow-y: auto;
}

.report-header {
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e6e8f0;
}

.report-header h2 {
  font-size: 20px;
  color: #1e3c72;
  margin-bottom: 5px;
}

.report-period {
  font-size: 14px;
  color: #666;
}

.report-content {
  flex: 1;
  padding: 20px;
}

.info-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.info-section h3 {
  font-size: 16px;
  color: #1e3c72;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e6e8f0;
}

.info-table {
  width: 100%;
  border-collapse: collapse;
}

.info-table td {
  padding: 8px;
  border: 1px solid #e6e8f0;
}

.info-table td:nth-child(odd) {
  background: #f5f7fa;
  font-weight: 600;
  width: 120px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f5f7fa;
  padding: 10px;
  font-size: 13px;
  color: #666;
  border: 1px solid #e6e8f0;
}

.data-table td {
  padding: 10px;
  text-align: center;
  border: 1px solid #e6e8f0;
}

.chart-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.chart-section h3 {
  font-size: 16px;
  color: #1e3c72;
  margin-bottom: 15px;
}

#financialChart {
  width: 100%;
  height: 300px;
}

.report-footer {
  padding: 20px;
  background: white;
  border-top: 1px solid #e6e8f0;
  text-align: right;
}

@media (max-width: 992px) {
  .sidebar {
    width: 220px;
  }

  .search-box {
    width: 250px;
  }

  .detail-panel {
    width: 350px;
  }
}

@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
  }

  .nav-menu {
    display: flex;
    overflow-x: auto;
    padding: 10px 0;
  }

  .nav-item {
    flex: 0 0 auto;
    border-left: none;
    border-bottom: 3px solid transparent;
    min-width: 120px;
  }

  .nav-item.active {
    border-left: none;
    border-bottom-color: #4dabf7;
  }

  .header {
    padding: 0 15px;
    height: 50px;
  }

  .content-area {
    padding: 15px;
    height: calc(100vh - 100px);
  }

  .card-body {
    padding: 15px;
  }

  .table-scroll-container {
    max-height: 500px;
  }

  .header-actions {
    gap: 10px;
  }

  .search-box {
    width: 200px;
  }

  .detail-panel {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    z-index: 100;
  }

  .main-content.with-detail-panel .content-wrapper {
    display: none;
  }
}

@media (max-width: 480px) {
  .logo-text {
    font-size: 18px;
  }

  .page-title {
    font-size: 16px;
  }
}

.el-table ::v-deep .caret-wrapper {
  width: 14px;
  height: 18px;
  margin-left: 2px;
}

.el-table ::v-deep .sort-caret.ascending {
  top: 2px;
}

.el-table ::v-deep .sort-caret.descending {
  bottom: 2px;
}

.pdf-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.pdf-preview-container {
  width: 100%;
  min-height: 720px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f7fa;
}

.pdf-preview-frame {
  width: 100%;
  height: 720px;
  background: #fff;
}

.pdf-empty-state {
  min-height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  gap: 12px;
}

.pdf-empty-state i {
  font-size: 42px;
}

.pdf-select-dialog {
  padding-top: 8px;
}

.pdf-select-tip {
  margin-bottom: 12px;
  color: #606266;
}

.pdf-radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pdf-radio-item {
  margin-right: 0;
}

.pdf-status-tag {
  padding: 8px 12px;
  border-radius: 999px;
  background: #f0f9eb;
  color: #67c23a;
  font-size: 12px;
  line-height: 1.4;
  max-width: 340px;
  word-break: break-all;
}
</style>