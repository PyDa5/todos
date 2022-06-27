# 发送邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_USE_SSL = True
# smpt服务地址
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 465

# 发送邮件的邮箱，需要配置开通SMTP
EMAIL_HOST_USER = '1174446068@qq.com'

# 此处的EMAIL_HOST_PASSWORD是用QQ邮箱授权码登录
EMAIL_HOST_PASSWORD = 'wtxzppxndaerfedf'

# 收件人看到的发件人
EMAIL_FROM = '1174446068@qq.com'
