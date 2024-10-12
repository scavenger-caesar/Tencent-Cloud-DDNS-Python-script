# 腾讯云DDNS脚本
## 1. 脚本功能介绍
可以将腾讯云上的域名动态映射到动态的IPv4或IPv6
## 2. 目录结构介绍
```
./
├── config.py           <---- 配置文件解析脚本
├── config.toml         <---- 配置文件
├── main.py             <---- 动态域名解析脚本
├── README.md
└── requirements.txt    <---- 依赖库清单
```
# 快速上手使用
使用前请先验证是否有公网IP, 否则映射域名后也无法正常访问;
## Linux环境
> tips: `$`不要复制，代表的是一行命令
### 1. 克隆此仓库
```shell
$ git clone https://github.com/scavenger-caesar/Tencent-Cloud-DDNS-Python-script.git
```
### 2. 安装依赖库
1. 进入克隆下来的仓库文件夹
```
$ cd ./Tencent-Cloud-DDNS-Python-script/
```
2. 安装依赖库
```
$ pip install -r ./requirements.txt
```

### 3. 设置config.toml配置文件
1. 获取腾讯云api key    
访问: https://console.cloud.tencent.com/cam/capi 获取api key

2. 把 api key 填入 config.toml
```toml
[api]
SecretId = "你的SecretId"
SecretKey = "你的SecretKey"
```
3. 把你的域名填入 config.toml
```toml
[dns]
# 一级域名
domain = "你的域名"
# 二级域名, 如不用二级域名则留空
sub_domain = ""
# 记录类型, 可选值: IPV6 | IPV4
record_type = "IPV6"
# 记录线路, 可选值: 参考官网DNS解析线路类型
record_line = "默认"
```

### 4. 运行ddns脚本
```shell
python3 ./main.py
```
## windows环境
TODO: 待补充

# 验证
如果能ping通，则配置动态域名解析成功

## ipv6
```shell
ping -6 <your domain>
```
## ipv4 
```shell
ping <your domain>
```
