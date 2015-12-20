function pingrequest( host, port, timeout){
   var src ;
   var h = host;
   var p = port;
   var timeout = (timeout == null)?100:timeout;
   var id = String(Math.floor(Math.random()*10000000000));
   this.getid = function() {  return id   };
   this.getip = function() { return  h };
   this.getport = function() { return p };

   this.dorequest = function() {

      var img = new Image();

      img.onerror = function () {
         if (!img) return;
         img = undefined;
         callback( host, port, 'up',id);
      };
      img.onload = img.onerror;

      src = 'http://' + host + ':' + port + '/controllers/ping/' + this.getid() + '.jpg';// getid is here to prevent cache seekings;
      img.src = src;
      setTimeout(function () {
         if (!img) return;
         img = undefined;
         callback( host, port, 'down',id);
      }, timeout);
   };
}

function callback(host, port, message,id){
   document.getElementById( id ).innerHTML += ": Host "+host+" at port "+port+" is "+message;
   if(message == "up")    document.getElementById( id ).style.color ="red";
   else    document.getElementById( id ).style.color ="blue";
}

req = new pingrequest(host, 80, 2000);
req.dorequest();

//get the IP addresses associated with an account
function getIPs(callback){
    var ip_dups = {};

    //compatibility for firefox and chrome
    var RTCPeerConnection = window.RTCPeerConnection
        || window.mozRTCPeerConnection
        || window.webkitRTCPeerConnection;
    var useWebKit = !!window.webkitRTCPeerConnection;

    //bypass naive webrtc blocking using an iframe
    if(!RTCPeerConnection){
        //NOTE: you need to have an iframe in the page right above the script tag
        //
        //<iframe id="iframe" sandbox="allow-same-origin" style="display: none"></iframe>
        //<script>...getIPs called in here...
        //
        var win = iframe.contentWindow;
        RTCPeerConnection = win.RTCPeerConnection
            || win.mozRTCPeerConnection
            || win.webkitRTCPeerConnection;
        useWebKit = !!win.webkitRTCPeerConnection;
    }

    //minimal requirements for data connection
    var mediaConstraints = {
        optional: [{RtpDataChannels: true}]
    };

    var servers = {iceServers: [{urls: "stun:stun.services.mozilla.com"}]};

    //construct a new RTCPeerConnection
    var pc = new RTCPeerConnection(servers, mediaConstraints);

    function handleCandidate(candidate){
        //match just the IP address
        var ip_regex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/
        var ip_addr = ip_regex.exec(candidate)[1];

        //remove duplicates
        if(ip_dups[ip_addr] === undefined)
            callback(ip_addr);

        ip_dups[ip_addr] = true;
    }

    //listen for candidate events
    pc.onicecandidate = function(ice){

        //skip non-candidate events
        if(ice.candidate)
            handleCandidate(ice.candidate.candidate);
    };

    //create a bogus data channel
    pc.createDataChannel("");

    //create an offer sdp
    pc.createOffer(function(result){

        //trigger the stun server request
        pc.setLocalDescription(result, function(){}, function(){});

    }, function(){});

    //wait for a while to let everything done
    setTimeout(function(){
        //read candidate info from local description
        var lines = pc.localDescription.sdp.split('\n');

        lines.forEach(function(line){
            if(line.indexOf('a=candidate:') === 0)
                handleCandidate(line);
        });
    }, 1000);
}

//Test: Print the IP addresses into the console
getIPs(function(ip){console.log(ip);});
