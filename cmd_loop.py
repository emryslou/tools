"""批量不依赖命令行执行
功能:
    1. 可以多次提交命令
    2. 多个命令排队执行
    3. 如果执行失败，则在其他命令执行后重试
"""
import datetime
import logging
import multiprocessing
import select
import socket
import subprocess
import sys
import threading
import time
import uuid


LOGGER = logging.getLogger(__name__)

class Command:
    def __init__(self, cmd, retry_times=10, timeout=40):
        self.cmd = cmd
        self.id = uuid.uuid4().__str__()
        self.run_times = 0
        self.sleep_secs = 0
        self.retry_times = retry_times or 10
        self.run_timeout = min(timeout or 10, 600)
        self.return_code = -1
        self.run_start = None
        self.run_end = None
    
    def __str__(self):
        return f'{self.id}(`{self.cmd}`)'
    
    def run(self):
        # 超过重试次数后停止
        if self.retry_times <= self.run_times:
            self.return_code = 257
            return None
        
        # 冷却时间
        if self.sleep_secs > 0:
            time.sleep(self.sleep_secs)
        self.run_times += 1
        self.sleep_secs = 1.3 ** self.run_times
        LOGGER.info(f'`{self}`:> -------------------------------------------')
        
        """日志输出"""
        def lines_logger_func(lines, func):
            [func(f'{self.cmd}:>\t{line}') for line in lines]
        
        """捕获输出，尽可能保证实时输出"""
        def capture_output_realtime(proc: subprocess.Popen):            
            while True:
                try:
                    rlist, _, _ = select.select([proc.stdout, proc.stderr], [], [], 0.05)
                    if proc.stdout in rlist:
                        for line in proc.stdout:
                            lines_logger_func(['cor:' + line.decode('utf-8', errors='ignore').strip()], LOGGER.info)
                    if proc.stderr in rlist:
                        for line in proc.stderr:
                            lines_logger_func(['cor:' + line.decode('utf-8', errors='ignore').strip()], LOGGER.error)
                except ValueError:
                    # 输出管道关闭，则退出
                    break
        
        proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, start_new_session=True)
        realtime_out = threading.Thread(target=capture_output_realtime, args=(proc,))
        self.run_start = datetime.datetime.now()
        try:
            realtime_out.start()
            out, err = proc.communicate(timeout=self.run_timeout)
            
            while realtime_out.is_alive(): pass
            
            self.return_code = proc.returncode
            if out:
                lines_logger_func(out.decode("utf-8", errors='ignore').split('\n'), LOGGER.info)
            if err:
                lines_logger_func(err.decode("utf-8").split('\n'), LOGGER.error)
            
        except subprocess.TimeoutExpired as e:
            LOGGER.warning(f'`{self}`:> exe timeout, {e}')
            proc.kill()
            time.sleep(0.5)
            # 主动关闭管道
            proc.stdout.close()
            proc.stderr.close()
            
            self.return_code = 256
        except BaseException as e:
            LOGGER.error(f'unknown {e}')
            
        self.run_end = datetime.datetime.now()
    
    def stat(self):
        return self.return_code, self.run_end - self.run_start, self.retry_times

CMD_QUEUE = multiprocessing.SimpleQueue()
CMD_INFO = {}
def cmd_queue_custom():
    """消费队列"""
    while True:
        cmd_id = CMD_QUEUE.get()
        cmd = CMD_INFO[cmd_id]
        cmd.run()
        run_status, elapsed, _ = cmd.stat()
        if run_status in [0, 256, 257]: # 退出状态
            match run_status:
                case 0: # 脚本正常退出
                    LOGGER.info(f'run {cmd} done, elapsed: {elapsed}')
                case 257: # 重试多次后仍然失败
                    LOGGER.error(f'run {cmd} failed, code:{run_status}, elapsed: {elapsed}, failed too many times')
                case 256: # 脚本执行超时
                    LOGGER.error(f'run {cmd} failed, code:{run_status}, elapsed: {elapsed}, execute timeout')
            del CMD_INFO[cmd_id]
        else: # 重试
            if elapsed > datetime.timedelta(seconds=min(cmd.run_timeout - 10, 10)): # 脚本执行一定时间，则多给一次重试机会
                cmd.run_times -= 1
            LOGGER.warning(f'run {cmd} failed, code:{run_status}, elapsed: {elapsed}, will retry it later')
            CMD_QUEUE.put(cmd_id)   
            
            
def cmd_queue_add(cmd):
    CMD_QUEUE.put(cmd.id)
    CMD_INFO[cmd.id] = cmd

def build_cmd_srv(addr):
    """构建通道"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(1)
    LOGGER.info('wait for cmd')
    handler = threading.Thread(target=cmd_queue_custom)
    handler.start()
    
    while True:
        try:
            recv_sock, _ = sock.accept()
            cmd_bytes = recv_sock.recv(1024)
            cmd = cmd_bytes.decode('utf-8').strip()
            if cmd == '>ping':
                recv_sock.send('<pong'.encode('utf-8'))
            else:
                cmd_obj = Command(cmd)
                CMD_INFO[cmd_obj.id] = cmd_obj
                CMD_QUEUE.put(cmd_obj.id)
                recv_sock.send(f'<recv(id:{cmd_obj.id})'.encode('utf-8'))
            recv_sock.close()
        except KeyboardInterrupt:
            break

def socket_sniff(addr, cmd):
    """嗅探通道，并尝试提交命令"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr)
        if len(cmd.strip()) > 0:
            sock.send(cmd.encode('utf-8'))
            msg = sock.recv(1024)
            msg = msg.decode('utf-8')
            LOGGER.info(f'{cmd}: {msg}')
        return True
    except ConnectionRefusedError:
        return False

def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s--%(levelname)s]%(message)s', stream=sys.stdout)
    
    addr = ("localhost", 12345)
    cmd = ' '.join(sys.argv[1:])
    if not socket_sniff(addr, cmd):
        try:
            handler = threading.Thread(target=build_cmd_srv, args=(addr,))
            handler.start()
            socket_sniff(addr, cmd)
            handler.join()
        except KeyboardInterrupt:
            LOGGER.info('Bye^2')

if __name__ == '__main__':
    main()
