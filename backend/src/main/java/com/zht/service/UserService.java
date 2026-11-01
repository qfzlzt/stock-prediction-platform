package com.zht.service;


import com.baomidou.mybatisplus.extension.service.IService;
import com.zht.entity.User;
import com.zht.entity.UserVO;

public interface UserService extends IService<User> {

    int login(UserVO user);

    int insert(UserVO user);


}
