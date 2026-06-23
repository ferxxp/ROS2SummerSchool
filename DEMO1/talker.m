rosinit('http://localhost:11311', 'NodeHost', '127.0.0.1')

pub = rospublisher('/chatter', 'std_msgs/String');
msg = rosmessage(pub);

for i = 1:100
    msg.Data = sprintf('Hello from MATLAB! #%d', i);
    send(pub, msg);
    fprintf('[talker] Sent: %s\n', msg.Data);
    pause(1);
end

rosshutdown
