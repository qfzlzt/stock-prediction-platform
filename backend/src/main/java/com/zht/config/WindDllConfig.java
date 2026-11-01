package com.zht.config;

import com.wind.api.W;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Bean;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.io.File;

@Configuration
public class WindDllConfig {

    private boolean windReady = false;

    @PostConstruct
    public void init() {
        System.out.println("========== Wind DLL Config ==========");

        try {
            // 1. 设置DLL路径
            File dir = new File("native");
            String dllDir = dir.getAbsolutePath();

            // 检查目录是否存在
            if (!dir.exists()) {
                System.err.println("❌ native目录不存在: " + dllDir);
                System.err.println("当前工作目录: " + System.getProperty("user.dir"));
                return;
            }

            System.out.println("native目录: " + dllDir);
            System.out.println("目录存在: " + dir.exists());

            // 2. 检查DLL文件
            File dllFile = new File(dir, "WindJava.dll");
            boolean dllExists = dllFile.exists();
            System.out.println("WindJava.dll存在: " + dllExists);

            if (!dllExists) {
                System.err.println("❌ WindJava.dll 文件不存在!");
                return;
            }

            System.out.println("DLL文件路径: " + dllFile.getAbsolutePath());
            System.out.println("DLL文件大小: " + dllFile.length() + " bytes");

            // 3. 设置系统属性
            System.setProperty("jna.library.path", dllDir);
            System.setProperty("java.library.path", dllDir);

            // 4. 加载DLL
            System.load(dllFile.getAbsolutePath());
            System.out.println("✅ DLL加载成功!");

            // 5. 启动Wind API
            startWind();

        } catch (UnsatisfiedLinkError e) {
            System.err.println("❌ DLL加载失败: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("❌ 初始化异常: " + e.getMessage());
            e.printStackTrace();
        }

        System.out.println("====================================");
    }

    /**
     * 启动Wind API
     */
    private void startWind() {
        try {
            System.out.println("正在启动Wind API...");
            long errorCode = W.start();

            if (errorCode == 0) {
                windReady = true;
                System.out.println("✅ Wind API启动成功!");

                // 测试连接
                testConnection();
            } else {
                windReady = false;
                System.err.println("❌ Wind API启动失败，错误码: " + errorCode);
                System.err.println("请检查Wind终端是否已启动并登录");
            }
        } catch (Exception e) {
            windReady = false;
            System.err.println("❌ Wind API启动异常: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 测试Wind连接
     */
    private void testConnection() {
        try {
            System.out.println("测试Wind连接...");

            // 用简单的wsd请求测试连接
            String testCode = "000001.SZ";
            String testDate = "2026-03-17";
            String testFields = "close";

            com.wind.api.struct.WindData windData = W.wsd(
                    testCode,
                    testFields,
                    testDate,
                    testDate,
                    ""
            );

            if (windData != null && windData.getErrorId() == 0) {
                System.out.println("✅ Wind连接测试成功!");
            } else {
                System.err.println("⚠️ Wind连接测试失败: " +
                        (windData != null ? windData : "返回null"));
            }

        } catch (Exception e) {
            System.err.println("⚠️ Wind连接测试异常: " + e.getMessage());
        }
    }

    /**
     * 获取Wind就绪状态
     */
    public boolean isWindReady() {
        return windReady;
    }

    /**
     * 停止Wind API
     */
    @PreDestroy
    public void destroy() {
        if (windReady) {
            try {
                System.out.println("正在关闭Wind API...");
                W.stop();
                System.out.println("✅ Wind API已关闭");
            } catch (Exception e) {
                System.err.println("❌ 关闭Wind API失败: " + e.getMessage());
            }
        }
    }

    /**
     * 提供Wind就绪状态的Bean
     */
    @Bean
    public WindReadyChecker windReadyChecker() {
        return new WindReadyChecker() {
            @Override
            public boolean isReady() {
                return windReady;
            }

            @Override
            public void ensureReady() {
                if (!windReady) {
                    throw new IllegalStateException("Wind API未就绪，请检查Wind终端是否已启动并登录");
                }
            }
        };
    }

    /**
     * Wind就绪状态检查接口
     */
    public interface WindReadyChecker {
        boolean isReady();
        void ensureReady();
    }
}