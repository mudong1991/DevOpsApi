# master 主机地址
read -p "Input Master IP: " MIP    ###指定masterIP
while [ ! -n "$MIP" ]
do
	read -p "Input Master IP: " MIP 
done
COMM1="sed -i \"s/#master: salt/master: $MIP/\" /etc/salt/minion"
eval $COMM1

# minion 的id
IP=`ifconfig eth1 | grep -i bcast | awk '{print $2}'| awk  -F : '{print $2}'`
if  [ ! -n "$IP" ] ;then
	IP=`ifconfig eth0 | grep -i bcast | awk '{print $2}'| awk  -F : '{print $2}'`
fi


echo ' '
read -p "Input Minion ID(default ip address): " MID  ###修改minion ID
if  [ ! -n "$MID" ] ;then
        COMM2="sed -i \"s/#id:.*/id: $IP/\" /etc/salt/minion"
else
        COMM2="sed -i \"s/#id:.*/id: $MID/\" /etc/salt/minion"
fi
eval $COMM2

###  开启日志
sed -i "s@#log_file: /var/log/salt/minion@log_file: /var/log/salt/minion@1" /etc/salt/minion
sed -i '488d' /etc/salt/minion
#
sed -i "s@#key_logfile: /var/log/salt/key@key_logfile: /var/log/salt/key@" /etc/salt/minion
#
echo ' '
echo -e "\033[42;37m Salt-minion Information: \033[0m"
echo '##############################'
sed -e '/^#/d;/^$/d' /etc/salt/minion
echo '##############################'
echo ' '
###启动服务
service salt-minion restart
chkconfig salt-minion on
###只要有新的minion客户端添加进来我们运行这个脚本就可快速完成minion端的配置啦.