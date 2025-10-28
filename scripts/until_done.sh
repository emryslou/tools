#!/bin/bash

# 在脚本报错后尝试
# 如果成功再退出，失败最多10次后也退出

RETRY_TIMES=100
A=$RETRY_TIMES

while true
do
	$@;
	if [[ $? -eq 0 ]]; then
		echo "执行成功";
		break ;
	else
		A=$((A - 1));
		if [[ $A -le 0 ]]; then
			echo "执行异常次数过多(超过了$RETRY_TIMES 次)";
			break ;
		else
			sleep 2;
			echo "第`expr $RETRY_TIMES - $A`次尝试再次执行 $@ ...";
		fi
	fi
done
