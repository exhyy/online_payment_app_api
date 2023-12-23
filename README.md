# online_payment_app_api

北京交通大学《数据库系统原理》课程设计应用服务器代码，基于Django构建，请参考[官方文档](https://docs.djangoproject.com/zh-hans/5.0/)。
前端[在这里](https://github.com/exhyy/online_payment_app)。

## 使用

### 安装Python依赖
本项目使用Python 3.18.16，需运行在linux服务器下
运行`pip install -r requirements.txt`安装依赖

### 安装redis
本项目需要使用redis作为应用服务器缓存
```bash
sudo apt update
sudo apt install redis-server
```

### 连接数据库服务器
在项目根目录下新建`my.cnf`文件（该文件会被git忽略），然后按照MySQL服务器配置的格式填写即可。示例如下：
```
[client]
host = 10.101.1.50
database = online_payment
user = xiaoming
password = 123456
default-character-set = utf8
```

### 配置并发支持
本应用服务器通过gunicorn实现并发，配置文件为`gunicorn_conf.py`。bind表示服务器端口，workers控制进程数。

### 启动服务器
部署命令如下：
```bash
PYTHONPATH=<项目上级目录> gunicorn -c gunicorn_conf.py online_payment_api.wgsi:application
```
如果只想使用单进程，或者需要调试服务器，则直接运行：
```bash
python manage.py runserver
```
