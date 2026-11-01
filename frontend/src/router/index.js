import Vue from 'vue'
import Router from 'vue-router'
import Register from "@/components/Register"
import Login from "@/components/Login"
import Index from "@/components/Index"
import companydetail from "@/components/company_Detail"
import KcbIndex from "@/components/KcbIndex"
// import Home from "@/components/home"
//解决vue-router 3.0以上 重复路由报错的问题
const originalPush = Router.prototype.push
Router.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err)
}
Vue.use(Router)

export default new Router({
  routes: [
	  {
	  		 path: "/",
	  		 component: Login
	  },
	  {
	  		 path: "/Register",
	  		 component: Register
	  },
	  
	  {
	  		 path: "/Login",
	  		 component: Login
	  },
	  {
	  		 path: "/Index",
	  		 component: Index
	  },
	  {
	  		 path: "/companydetail",
	  		 component: companydetail
	  },
	  {
	  		 path: "/kcb-index",
	  		 component: KcbIndex
	  },
	  // {
	  // 		 path: "/Home",
	  // 		 component: Home
	  // },
   ]
})