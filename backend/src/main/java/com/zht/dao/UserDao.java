package com.zht.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zht.entity.User;
import com.zht.entity.UserVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface UserDao extends BaseMapper<User> {

    User findByUserName(@Param("username")String username);
    int insertOne(UserVO user);
}
