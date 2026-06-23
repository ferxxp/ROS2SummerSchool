core=ros.Core

rosinit('127.0.0.1',11311,'NodeName','/test_node')

sub = rossubscriber('/chatter', 'std_msgs/String', @listenerCallback);

fprintf('[listener] Listening on /chatter. Press Ctrl+C to stop.\n');
while true
    pause(1);
end

function listenerCallback(~, msg)
    fprintf('[listener] Received: %s\n', msg.Data);
end
