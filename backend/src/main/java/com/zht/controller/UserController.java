package com.zht.controller;

import com.zht.commons.r.R;
import com.zht.entity.UserVO;
import com.zht.service.UserService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@RequestMapping("/user")
@Controller
@Slf4j
public class UserController {

    @Autowired
    private UserService userService;


    @PostMapping("/login")
    @ResponseBody
    public R login(@RequestBody  UserVO user){

        log.info("user登录-{}",user);
        return R.succ(userService.login(user));

    }

    @PostMapping("/register")
    @ResponseBody
    public  R register(@RequestBody UserVO user){
        log.info("user注册-{}",user);
        return R.succ(userService.insert(user));
    }






}
