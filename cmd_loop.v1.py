import logging.handlers
import multiprocessing
import multiprocessing.queues
import sys
import logging
import subprocess
import datetime
import threading
import socket
import uuid
import queue
import select

logger = logging.getLogger(__name__)

cmd_queue = multiprocessing.SimpleQueue()
cmd_info = {}

class Command(object):
    def __init__(self, cmd, retry_times: int = 10, timeout: int = 10) -> None:
        self.cmd = cmd
        self.id = uuid.uuid4().__str__()
        self.retry_times = retry_times or 10
        self.run_timeout = max(timeout or 10, 600)
        self.return_code = -1
        self.run_start = None
        self.run_end = None
    
    def __str__(self) -> str:
        return f'{self.id}(`{self.cmd}`)'
    
    def run(self):
        if self.retry_times <= 0:
            logger.error(f'`{self}`:> run failed too many times')
            return None
        self.retry_times -= 1

        self.run_start = datetime.datetime.now()
        logger.info(f'`{self}`:>\t-------------------------------------------')
        def is_continue(event: queue.Queue) -> bool:
            try:
                return event.get_nowait() != True
            except Exception as e:
                return isinstance(e, queue.Empty)
        
        def logger_func(lines, func):
            [func(f'`{self.cmd}`:>>\t{line}') for line in lines]
            
        def capture_output(proc: subprocess.Popen, event: queue.Queue):
            while True:
                if not is_continue(event):
                    break
                try:
                    rlist, _, _ = select.select([proc.stdout, proc.stderr], [], [], 0.1)
                    if proc.stdout in rlist:
                        logger_func([line.decode('utf-8').strip() for line in proc.stdout.readlines()], logger.info)
                    if proc.stderr in rlist:
                        logger_func([line.decode('utf-8').strip() for line in proc.stderr.readlines()], logger.error)
                except ValueError:
                    pass
        
        q = queue.Queue()
        
        proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, start_new_session=True)
        handler = threading.Thread(target=capture_output, args=(proc, q))
        try:
            handler.start()
            out, err = proc.communicate(timeout=86400)
            q.put(True)
            
            # 保证输出顺序正确
            while handler.is_alive(): continue
            
            # 输出剩余结果
            if out: logger_func(out.decode('utf-8').split('\n'), logger.info)
            if err: logger_func(err.decode('utf-8').split('\n'), logger.error)
            
            logger.info(f'`{self}`:>\t-------------------------------------------')
            
            self.return_code = proc.returncode
        except subprocess.TimeoutExpired as e:
            logger.warning(f'`{self}`:> exe timeout, {e}')
            proc.kill()
            q.put(True)
            self.return_code = 256
        except BaseException as e:
            logger.error(f'unknown {e}')
            
        self.run_end = datetime.datetime.now()
    
    def stat(self):
        return self.return_code, self.run_end - self.run_start, self.retry_times

def cmd_queue_custom():
    while True:
        cmd_id = cmd_queue.get()
        cmd = cmd_info[cmd_id]
        cmd.run()
        run_status, elapsed, _ = cmd.stat()
        if run_status > 0:
            if run_status != 256 and cmd.retry_times > 0:
                logger.warning(f'run {cmd} failed, code:{run_status}, elapsed: {elapsed}, will retry it later')
                cmd_queue_add(cmd_id)
            else:
                logger.error(f'run {cmd} failed, code:{run_status}, elapsed: {elapsed}, retry too many times or elapsed too long')
                del cmd_info[cmd_id]
        else:
            logger.info(f'run {cmd} done, elapsed: {elapsed}')
            del cmd_info[cmd_id]

def cmd_queue_add(cmd):
    cmd_queue.put(cmd)

def build_cmd_srv(addr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(addr)
    sock.listen(1)
    logger.info(f'wait for cmd')
    handler = threading.Thread(target=cmd_queue_custom)
    handler.start()
    
    """
    创建服务
    """
    while True:
        try:
            recv_sock, _ = sock.accept()
            cmd_bytes = recv_sock.recv(1024)
            cmd = cmd_bytes.decode('utf-8').strip()
            if cmd == '>ping': recv_sock.send('<pong'.encode('utf-8'))
            else:
                cmd = Command(cmd)
                cmd_info[cmd.id] = cmd
                cmd_queue_add(cmd.id)
                recv_sock.send(f'<recv(id:{cmd.id})'.encode('utf-8'))
            recv_sock.close()
        except KeyboardInterrupt:
            break

def socket_sniff(addr, cmd: str):
    """尝试嗅探网络，并发送需要执行的命令"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr)
        if len(cmd.strip()) > 0:
            sock.send(cmd.encode('utf-8'))
            msg = sock.recv(1024)
            msg = msg.decode('utf-8')
            logger.info(f'{cmd}: {msg}')
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
            logger.info('Bye^2')

if __name__ == '__main__':
    main()
