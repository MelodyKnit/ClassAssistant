CREATE TABLE IF NOT EXISTS faculty_table (
    faculty VARCHAR(30) PRIMARY KEY COMMENT '院系',
    invitee VARCHAR(99) NOT NULL COMMENT '添加人'
);

CREATE TABLE IF NOT EXISTS teacher (
    name VARCHAR(20) NOT NULL COMMENT '教师姓名',
    qq BIGINT PRIMARY KEY  COMMENT '教师qq号',
    invitee VARCHAR(99) NOT NULL COMMENT '添加人',
    telephone BIGINT NOT NULL UNIQUE COMMENT '教师电话'
);

CREATE TABLE IF NOT EXISTS expertise_table (
    faculty VARCHAR(30) NOT NULL COMMENT '院系',
    expertise VARCHAR(60) PRIMARY KEY COMMENT '专业',
    FOREIGN KEY (faculty) REFERENCES faculty_table(faculty)
);

CREATE TABLE IF NOT EXISTS class_table (
    class_id BIGINT NOT NULL COMMENT '班级号',
    expertise VARCHAR(60) NOT NULL COMMENT '专业',
    class_group BIGINT NOT NULL UNIQUE COMMENT '班级QQ群',
    class_name VARCHAR(255) PRIMARY KEY COMMENT '班级群名',
    class_teacher BIGINT NOT NULL COMMENT '班主任QQ',
    FOREIGN KEY (class_teacher) REFERENCES teacher(qq),
    FOREIGN KEY (expertise) REFERENCES expertise_table(expertise)
);

CREATE TABLE IF NOT EXISTS score_log (
    class_name VARCHAR(255) NOT NULL COMMENT '班级群名',
    score_type VARCHAR(50) COMMENT '分数类型',
    explain_reason TEXT COMMENT '解释原因原因',
    name VARCHAR(20) NOT NULL COMMENT '学生姓名',
    student_id BIGINT NOT NULL COMMENT '学生学号',
    score INT COMMENT '加减的分数',
    qq BIGINT NOT NULL COMMENT '学生qq',
    log_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '日志时间',
    prove VARCHAR(255) DEFAULT "" COMMENT "证明文件"
);

CREATE TABLE IF NOT EXISTS user_info (
    姓名 VARCHAR(20) NOT NULL COMMENT '学生姓名',
    班级 VARCHAR(255) NOT NULL COMMENT '班级名称',
    序号 INT NOT NULL COMMENT '个人在班级中的序号',
    学号 BIGINT NOT NULL COMMENT '学号',
    性别 VARCHAR(10) NOT NULL COMMENT '性别',
    联系方式 BIGINT NOT NULL COMMENT "学生联系方式",
    身份证号 VARCHAR(20) COMMENT '学生身份证',
    出生日期 TIMESTAMP COMMENT '出生日期',
    寝室 VARCHAR(10) COMMENT '寝室号',
    寝室长 VARCHAR(5) COMMENT '是否为寝室长',
    微信 VARCHAR(100) COMMENT '微信号',
    QQ BIGINT PRIMARY KEY COMMENT 'QQ',
    邮箱 VARCHAR(100) COMMENT '邮箱号',
    民族 VARCHAR(200) COMMENT '民族',
    籍贯 VARCHAR(200)  COMMENT '籍贯',
    职位 VARCHAR(50) NOT NULL DEFAULT '学生' COMMENT '学生',
    团员 VARCHAR(10) COMMENT '是否为团员',
    入党积极分子 VARCHAR(10) COMMENT '是否为入党积极分子',
    团学 VARCHAR(100) COMMENT '团学干部',
    社团 VARCHAR(200) COMMENT '加入的社团',
    分数 INT NOT NULL DEFAULT 0 COMMENT '分数',
    FOREIGN KEY (班级) REFERENCES class_table(class_name)
);

CREATE TABLE IF NOT EXISTS shop (
    teacher BIGINT NOT NULL COMMENT '教师QQ',
    shop_name VARCHAR(255) NOT NULL COMMENT '商品',
    shop_price INT NOT NULL DEFAULT 0 COMMENT '商品价格',
    FOREIGN KEY (teacher) REFERENCES teacher(qq)
);


CREATE TABLE IF NOT EXISTS receiving (
    title VARCHAR(255) NOT NULL COMMENT '收取标题',
    type VARCHAR(255) NOT NULL COMMENT '收取类型',
    class_name VARCHAR(255) NOT NULL COMMENT '班级名称',
    initiate BIGINT NOT NULL COMMENT '发起人',
    completed boolean NOT NULL DEFAULT FALSE COMMENT '是否已经完成',
    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
);


CREATE TABLE IF NOT EXISTS receiving_pictures (
    title VARCHAR(255) NOT NULL COMMENT '收取标题',
    user_id BIGINT NOT NULL COMMENT '提交人QQ',
    user_name VARCHAR(20) NOT NULL COMMENT '提交人姓名',
    class_name VARCHAR(255) NOT NULL COMMENT '班级名称',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名称md5',
    create_time TIMESTAMP NOT NULL COMMENT '创建时间',
    push_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间'
);


CREATE TABLE IF NOT EXISTS cost (
    thing TEXT NOT NULL COMMENT '费用所花费在某件事情',
    money DOUBLE NOT NULL COMMENT '花费金额',

)

