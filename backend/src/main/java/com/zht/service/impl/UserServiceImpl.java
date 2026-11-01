package com.zht.service.impl;


import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zht.commons.exception.ServiceException;
import com.zht.commons.r.Codes;
import com.zht.dao.UserDao;
import com.zht.entity.User;
import com.zht.entity.UserVO;
import com.zht.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service("userService")
public class UserServiceImpl extends ServiceImpl<UserDao,User> implements UserService {

    @Autowired
    private UserDao userDao;

    @Override
    public int insert(UserVO user) {
        User one= userDao.findByUserName(user.getUsername());
        if(one!=null){
            throw new ServiceException(Codes.USER_EXISTS);
        }
        return userDao.insertOne(user);
    }

    @Override
    public int login(UserVO user) {
        User one = userDao.findByUserName(user.getUsername());
        if(null==one){
            throw new ServiceException(Codes.USER_ERROR);
        }
        if(!user.getPassword().equals(one.getPassword())){
            throw new ServiceException(Codes.LOGIN_FAIL);
        }


        return 1;
    }
}
