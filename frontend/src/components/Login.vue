<template>
	<div id="l_app">
	    <div class="main_div">
	        <div class="info_div">
	            <div>
	                <div class="logo">股票<span>预测</span></div>
	                <div class="subtitle">AI驱动的股票预测分析平台</div>
	                <table class="table_cls">
	                    <tr>
	                        <td>账号：</td>
	                        <td><el-input v-model="form.username" placeholder="请输入账号" /></td>
	                    </tr>
	                    <tr>
	                        <td>密码：</td>
	                        <td><el-input show-password v-model="form.password" placeholder="请输入密码" /></td>
	                    </tr>
	                </table>
	                <el-button class="login_btn" @click="login()" type="primary">登录</el-button>
	                
	                <div class="features">
	                    <div class="feature-item">
	                        <svg class="feature-icon" viewBox="0 0 24 24" fill="currentColor">
	                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
	                        </svg>
	                        <span>AI预测</span>
	                    </div>
	                    <div class="feature-item">
	                        <svg class="feature-icon" viewBox="0 0 24 24" fill="currentColor">
	                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
	                        </svg>
	                        <span>实时数据</span>
	                    </div>
	                    <div class="feature-item">
	                        <svg class="feature-icon" viewBox="0 0 24 24" fill="currentColor">
	                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
	                        </svg>
	                        <span>专业分析</span>
	                    </div>
	                </div>
	            </div>
	            <div class="bottom_div">
	                <span @click="goPage('/Register')">注册新用户</span>
	            </div>
	        </div>
	        
	        <div class="stock-chart">
	            <div class="chart-line"></div>
	        </div>
	    </div>
	</div>
</template>

<script>
	export default {
		data(){
			return {
				form:{
					username:"",
					password:"",
				}
			
			}
			
		},
		methods:{
			goPage(url){
				this.$router.push(url)
			},
			login(){
				this.axios({
					method:"POST",
					url:"http://localhost:9090/user/login",
					data:this.form
				}).then((result)=>{
					var r = result.data;
					if(r.code==200){
						
						this.$message({
							message:"登陆成功",
							type:"success"
						})
						this.$router.push("/Index");
					}else{
						this.$message({
							message:r.msg,
							type:"error"
						})
					}
				})
			},
		}
	}
</script>

<style>
	* {
	    margin: 0;
	    padding: 0;
	    box-sizing: border-box;
	    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
	}
	
	/* 确保 html 和 body 完全覆盖 */
	html, body {
	    margin: 0;
	    padding: 0;
	    width: 100%;
	    height: 100%;
	    overflow-x: hidden;
	}
	
	#l_app{
		width: 100%;
	    height: 100%;
		background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
		position: fixed;
		top: 0;
		left: 0;
		overflow-y: auto;
		overflow-x: hidden;
	}
	
	.main_div {
	    width: 100%;
	    min-height: 100%;
	    display: flex;
	    justify-content: center;
	    align-items: center;
	    position: relative;
	    padding: 20px;
	}
	
	.main_div::before {
	    content: '';
	    position: absolute;
	    top: 0;
	    left: 0;
	    right: 0;
	    bottom: 0;
	    background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23000000" fill-opacity="0.1" d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,192C672,181,768,139,864,138.7C960,139,1056,181,1152,181.3C1248,181,1344,139,1392,117.3L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
	    background-size: cover;
	    background-position: center;
	    pointer-events: none;
	}
	
	.info_div {
	    width: 420px;
	    background-color: rgba(255, 255, 255, 0.95);
	    border-radius: 12px;
	    padding: 30px;
	    display: flex;
	    flex-direction: column;
	    justify-content: space-between;
	    align-items: center;
	    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
	    z-index: 10;
	    position: relative;
	}
	
	.logo {
	    font-size: 28px;
	    font-weight: 700;
	    margin-bottom: 10px;
	    color: #1e3c72;
	    text-align: center;
	}
	
	.logo span {
	    color: #4dabf7;
	}
	
	.subtitle {
	    color: #666;
	    margin-bottom: 25px;
	    text-align: center;
	    font-size: 14px;
	}
	
	.table_cls {
	    width: 100%;
	    margin: 15px 0;
	}
	
	.table_cls tr td {
	    padding: 12px 5px;
	    vertical-align: middle;
	}
	
	.table_cls tr td:first-child {
	    width: 70px;
	    font-weight: 500;
	    color: #333;
	}
	
	.login_btn {
	    width: 100%;
	    height: 45px;
	    font-size: 16px;
	    font-weight: 600;
	    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
	    border: none;
	    margin-top: 10px;
	}
	
	.login_btn:hover {
	    opacity: 0.9;
	}
	
	.bottom_div {
	    display: flex;
	    justify-content: center;
	    width: 100%;
	    color: #666;
	    font-weight: 500;
	    margin-top: 20px;
	    padding-top: 15px;
	    border-top: 1px solid #eee;
	}
	
	.bottom_div span {
	    color: #4dabf7;
	    cursor: pointer;
	    transition: color 0.3s;
	}
	
	.bottom_div span:hover {
	    color: #1e3c72;
	    text-decoration: underline;
	}
	
	.stock-chart {
	    position: absolute;
	    bottom: 0;
	    left: 0;
	    right: 0;
	    height: 120px;
	    background: rgba(0, 0, 0, 0.2);
	    overflow: hidden;
	    z-index: 1;
	}
	
	.chart-line {
	    position: absolute;
	    bottom: 0;
	    left: 0;
	    width: 100%;
	    height: 100%;
	    background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120" preserveAspectRatio="none"><path d="M0,90 Q300,30 600,90 T1200,30 L1200,120 L0,120 Z" fill="rgba(255,255,255,0.1)"/></svg>');
	    background-size: cover;
	}
	
	.features {
	    display: flex;
	    justify-content: space-around;
	    width: 100%;
	    margin-top: 20px;
	    color: #666;
	    font-size: 12px;
	}
	
	.feature-item {
	    display: flex;
	    flex-direction: column;
	    align-items: center;
	    text-align: center;
	}
	
	.feature-icon {
	    width: 24px;
	    height: 24px;
	    margin-bottom: 5px;
	    color: #4dabf7;
	}
	
	@media (max-width: 480px) {
	    .info_div {
	        width: 90%;
	        padding: 20px;
	    }
	}
</style>